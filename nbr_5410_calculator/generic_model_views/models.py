'''
Partial implementation of `QAbstractItemModel`.
'''

from collections.abc import Sequence
from contextlib import suppress
from enum import Enum
from operator import attrgetter
from typing import TypeVar, NamedTuple, Generic, Any, cast, overload, override

from PySide6.QtCore import (
	QAbstractItemModel,
	QMimeData,
	QModelIndex,
	QObject,
	QPersistentModelIndex,
	Qt,
)
from pydantic import TypeAdapter



# Type aliases.
T = TypeVar( 'T' )
ModelIndex = QModelIndex | QPersistentModelIndex



class Field( NamedTuple ):
	'''
	Field mapping for models.
	'''
	
	name: str
	label: str
	editable: bool = True
	setter: str = ''
	format: str = ''
	suffix: str = ''
	
	
	def typeIn( self, instance: Any ) -> type:
		'''
		Return type of `Field` in `instance`.
		'''
		
		return type( getattr( instance, self.setter or self.name ) )
	
	
	def getFrom( self, instance: Any ) -> Any:
		'''
		Return the value of `Field` in `instance`.
		'''
		
		return attrgetter( self.name )( instance )
	
	
	def setIn( self, instance: Any, value: Any ) -> None:
		'''
		Set value of `Field` in `instance`.
		'''
		
		setattr( instance, self.setter or self.name, self.typeIn( instance )( value ) )



class GenericItemModel( Generic[T], QAbstractItemModel ):
	'''
	Maps a list of generic objects to a `QAbstractItemView`.
	'''
	
	jsonMimeType = 'application/json'
	
	
	@override
	def __init__(
		self,
		fields: list[Field] | list[Field | None],
		datasource: list[T],
		childListName: str = '',
		childFields: list[Field] | list[Field | None] | None = None,
		parent: QObject | None = None,
	) -> None:
		super().__init__( parent )
		
		self.fields = fields
		self.datasource = datasource
		self.childListName = childListName
		self.childFields = childFields if childFields is not None else []
	
	
	def fieldFromIndex( self, index: ModelIndex ) -> Field | None:
		'''
		Return the `Field` associated with the given `index`.
		'''
		
		# Top-level item.
		if not index.parent().isValid():
			return self.fields[index.column()]
		
		# Sub-item.
		return self.childFields[index.column()]
	
	
	def itemFromIndex( self, index: ModelIndex ) -> T:
		'''
		Return the item associated with the given `index`.
		'''
		
		return cast( T, index.internalPointer() )
	
	
	def childList( self, item: T ) -> list[T]:
		'''
		Return the list of children for an `item` in the model.
		'''
		
		return getattr( item, self.childListName )
	
	
	@override
	def index( self, row: int, column: int, parent: ModelIndex = QModelIndex() ) -> QModelIndex:
		'''
		Return the index of the item in the model specified by the given `row`, `column` and
		`parent` index.
		'''
		
		# Top-level item.
		if not parent.isValid():
			if len( self.datasource ) > 0:
				return self.createIndex( row, column, self.datasource[row] )
			else:
				return QModelIndex()
		
		# Sub-item.
		parentItem = self.itemFromIndex( parent )
		if len( self.childList( parentItem ) ) > 0:
			childItem = self.childList( parentItem )[row]
		else:
			return QModelIndex()
		
		return self.createIndex( row, column, childItem )
	
	
	@overload
	def parent( self ) -> QObject: ...
	
	@overload
	def parent( self, child: ModelIndex ) -> QModelIndex: ...
	
	@override
	def parent( self, child: ModelIndex | None = None ) -> QModelIndex | QObject:
		'''
		Return the parent of the model item with the given `index`.
		'''
		
		# This is actually calling `QObject.parent()`, and not the virtual
		# `QAbstractItemModel.parent( child: ModelIndex )`.
		if child is None:
			return super().parent()
		
		# Iterate all children of top-level items.
		if self.childListName:
			item = self.itemFromIndex( child )
			
			for row, parentItem in enumerate( self.datasource ):
				if hasattr( parentItem, self.childListName ) and item in self.childList( parentItem ):
					return self.createIndex( row, 0, parentItem )
		
		# Top-level items have no parent.
		return QModelIndex()
	
	
	@override
	def columnCount( self, parent: ModelIndex = QModelIndex() ) -> int:
		'''
		Return the number of columns (`Field`s) in the model.
		'''
		
		_ = parent	# Unused.
		
		return len( self.fields )
	
	
	@override
	def rowCount( self, parent: ModelIndex = QModelIndex() ) -> int:
		'''
		Return the number of rows under the given `parent`.
		An invalid `parent` returns the number of top-level rows.
		'''
		
		# Top-level items.
		if not parent.isValid():
			return len( self.datasource )
		
		with suppress( AttributeError ):
			return len( self.childList( self.itemFromIndex( parent ) ) )
		
		return 0
	
	
	@override
	def flags( self, index: ModelIndex ) -> Qt.ItemFlag:
		'''
		Return flags for cells in table.
		'''
		
		flags = super().flags( index )
		
		if not index.isValid():
			return flags | Qt.ItemFlag.ItemIsDropEnabled
		
		field = self.fieldFromIndex( index )
		if field and field.editable:
			flags |= Qt.ItemFlag.ItemIsEditable
		
		if hasattr( self.itemFromIndex( index ), self.childListName ):
			flags |= Qt.ItemFlag.ItemIsDropEnabled
		
		return flags | Qt.ItemFlag.ItemIsDragEnabled
	
	
	@override
	def headerData( self, section: int, orientation: Qt.Orientation, role: int = 0 ) -> str | None:
		'''
		Return data for table headers.
		'''
		
		role = Qt.ItemDataRole( role )
		if role is not Qt.ItemDataRole.DisplayRole:
			return None
		
		if orientation is Qt.Orientation.Vertical:	# TODO: Remove this?
			return f'{section + 1}'
		
		field = self.fields[section] or self.childFields[section]
		assert field is not None
		
		return field.label
	
	
	@override
	def data( self, index: ModelIndex, role: int = 0 ) -> Any | None:
		'''
		Return data for table cells.
		'''
		
		role = Qt.ItemDataRole( role )
		if role not in { Qt.ItemDataRole.DisplayRole, Qt.ItemDataRole.EditRole } or not index.isValid():
			return None
		
		field = self.fieldFromIndex( index )
		item = self.itemFromIndex( index )
		
		# This column is only valid for a parent or child of this item.
		if not field:
			return None
		
		# Edit role.
		if role is Qt.ItemDataRole.EditRole:
			return field.getFrom( item )
		
		# Display role.
		match value := field.getFrom( item ):
			case Enum():
				return value.name
			
			case _:
				return f'{value:{field.format}}{field.suffix}'
	
	
	@override
	def setData( self, index: ModelIndex, value: Any, role: int = 0 ) -> bool:
		'''
		Update values in model.
		'''
		
		role = Qt.ItemDataRole( role )
		if role is not Qt.ItemDataRole.EditRole or not index.isValid():
			return False
		
		field = self.fieldFromIndex( index )
		item = self.itemFromIndex( index )
		assert field is not None
		
		with suppress( ValueError ):
			field.setIn( item, value )
			self.dataChanged.emit( index, index, [ role ] )
			
			return True
		
		return False
	
	
	def newItem( self ) -> T:
		'''
		Return a new item to be used with `insertRows`.
		'''
		
		raise NotImplementedError()
	
	
	def insertItem( self, item: T, row: int = -1, parent: ModelIndex = QModelIndex() ) -> None:
		'''
		Insert an existing item into the model's datasource.
		'''
		
		if parent.isValid():
			datasource = getattr( self.itemFromIndex( parent ), self.childListName )
		else:
			datasource = self.datasource
		
		if row < 0:
			row = len( datasource ) + 2 + row
		
		self.beginInsertRows( parent, row, row )
		datasource.insert( row, item )
		self.endInsertRows()
	
	
	@override
	def insertRows( self, row: int, count: int, parent: ModelIndex = QModelIndex() ) -> bool:
		'''
		Insert new items using `newItem`.
		'''
		
		for _ in range( count ):
			self.insertItem( self.newItem(), row, parent )
		
		return True
	
	
	@override
	def removeRows( self, row: int, count: int, parent: ModelIndex = QModelIndex() ) -> bool:
		'''
		Delete existing items.
		'''
		
		if parent.isValid():
			datasource = getattr( self.itemFromIndex( parent ), self.childListName )
		else:
			datasource = self.datasource
		
		self.beginRemoveRows( parent, row, row + count - 1 )
		for _ in range( count ):
			datasource.pop( row )
		self.endRemoveRows()
		
		return True
	
	
	@override
	def moveRows(
		self,
		sourceParent: ModelIndex,
		sourceRow: int,
		count: int,
		destinationParent: ModelIndex,
		destinationChild: int
	) -> bool:
		'''
		Move existing items.
		'''
		
		# Move to end.
		if destinationChild == -1:
			destinationChild = self.rowCount( destinationParent )
		
		if not self.beginMoveRows(
			sourceParent,
			sourceRow,
			sourceRow + count - 1,
			destinationParent,
			destinationChild
		) or destinationChild < 0 or destinationChild > self.rowCount( destinationParent ):
			return False
		
		if sourceParent.isValid():
			sourceDatasource = getattr( self.itemFromIndex( sourceParent ), self.childListName )
		else:
			sourceDatasource = self.datasource
		
		items: list[T] = []
		for _ in range( count ):
			items.append( sourceDatasource.pop( sourceRow ) )
		
		# Update destination after we removed items from the list.
		if destinationParent == sourceParent and destinationChild >= sourceRow:
			destinationChild -= count
		
		if destinationParent.isValid():
			destinationDatasource = getattr( self.itemFromIndex( destinationParent ), self.childListName )
		else:
			destinationDatasource = self.datasource
		
		for item in reversed( items ):
			destinationDatasource.insert( destinationChild, item )
		
		self.endMoveRows()
		
		return True
	
	
	@override
	def sort( self, column: int, order: Qt.SortOrder = Qt.SortOrder.AscendingOrder ) -> None:
		'''
		Sort items by specified field.
		'''
		
		reverse = order is not Qt.SortOrder.AscendingOrder
		key = attrgetter( self.fields[column].name )	# TODO: Fix for sub-items.
		
		self.layoutAboutToBeChanged.emit()
		self.datasource = sorted( self.datasource, key = key, reverse = reverse )
		self.layoutChanged.emit()
	
	
	@override
	def mimeTypes( self ) -> list[str]:
		'''
		Returns the list of allowed MIME types.
		'''
		
		return [ self.jsonMimeType ]
	
	
	@override
	def mimeData( self, indexes: Sequence[QModelIndex] ) -> QMimeData:
		'''
		Encode a list of items into supported MIME types.
		'''
		
		items = [ self.itemFromIndex( index ) for index in indexes if index.column() == 0 ]
		
		jsonBytes = TypeAdapter( list[T] ).dump_json( items )
		
		mimeData = QMimeData()
		mimeData.setData( self.jsonMimeType, jsonBytes )
		
		return mimeData
	
	
	@override
	def dropMimeData(
		self,
		data: QMimeData,
		action: Qt.DropAction,
		row: int,
		column: int,
		parent: ModelIndex
	) -> bool:
		'''
		Handles the data supplied by a drag and drop operation.
		'''
		
		match action:
			case Qt.DropAction.IgnoreAction:
				return True
			
			case Qt.DropAction.MoveAction | Qt.DropAction.CopyAction if data.hasFormat( self.jsonMimeType ):
				jsonBytes = data.data( self.jsonMimeType ).data()
				items = TypeAdapter( list[T] ).validate_json( jsonBytes )
				
				for item in reversed( items ):
					self.insertItem( item, row, parent )
				
				return True
			
			case _:
				return False
	
	
	@override
	def supportedDropActions( self ) -> Qt.DropAction:
		'''
		Return supported drop actions.
		'''
		
		return Qt.DropAction.MoveAction
	
	
	@override
	def supportedDragActions( self ) -> Qt.DropAction:
		'''
		Return supported drag actions.
		'''
		
		return Qt.DropAction.MoveAction