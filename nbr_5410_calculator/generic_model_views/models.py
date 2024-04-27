# 
# NBR 5410 Calculator
# 
# 
# Author: Marcelo Tellier Sartori Vaz <marcelotsvaz@gmail.com>



from typing import TypeVar, NamedTuple, Generic, Sequence, Any, cast, overload
from operator import attrgetter
from contextlib import suppress
from enum import Enum

from PySide6.QtCore import (
	Qt,
	QObject,
	QAbstractItemModel,
	QModelIndex,
	QPersistentModelIndex,
	QMimeData,
)



# Type aliases.
T = TypeVar('T')
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
	
	def __init__(
		self,
		fields: list[Field] | list[Field | None],
		datasource: list[T],
		childListName: str = '',
		childFields: list[Field] | list[Field | None] | None = None,
		parent: QObject | None = None,
	) -> None:
		super().__init__( parent )
		
		self.moveMimeType = 'application/vnd.set.row'
		
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
	
	
	def index( self, row: int, column: int, parent: ModelIndex = QModelIndex() ) -> QModelIndex:
		'''
		Return the index of the item in the model specified by the given `row`, `column` and
		`parent` index.
		'''
		
		# Top-level item.
		if not parent.isValid():
			try:
				return self.createIndex( row, column, self.datasource[row] )
			except IndexError:
				# Empty model.
				return QModelIndex()
		
		# Sub-item.
		parentItem = self.itemFromIndex( parent )
		childItem = self.childList( parentItem )[row]
		
		return self.createIndex( row, column, childItem )
	
	
	@overload
	def parent( self ) -> QObject: ...
	
	@overload
	def parent( self, child: ModelIndex ) -> QModelIndex: ...
	
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
	
	
	def columnCount( self, parent: ModelIndex = QModelIndex() ) -> int:
		'''
		Return the number of columns (`Field`s) in the model.
		'''
		
		_ = parent	# Unused.
		
		return len( self.fields )
	
	
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
	
	
	def flags( self, index: ModelIndex ) -> Qt.ItemFlag:
		'''
		Return flags for cells in table.
		'''
		
		flags = super().flags( index )
		
		if not index.isValid():
			return flags | Qt.ItemFlag.ItemIsDropEnabled
		
		if ( field := self.fieldFromIndex( index ) ) and field.editable:
			flags |= Qt.ItemFlag.ItemIsEditable
		
		return flags | Qt.ItemFlag.ItemIsDragEnabled
	
	
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
	
	
	def insertRows( self, row: int, count: int, parent: ModelIndex = QModelIndex() ) -> bool:
		'''
		Insert new items using `newItem`.
		'''
		
		if parent.isValid():
			datasource = getattr( self.itemFromIndex( parent ), self.childListName )
		else:
			datasource = self.datasource
		
		self.beginInsertRows( parent, row, row + count - 1 )
		for index in range( row, row + count ):
			datasource.insert( index, self.newItem() )
		self.endInsertRows()
		
		return True
	
	
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
			destinationChild = self.rowCount()
		
		if not self.beginMoveRows(
			sourceParent,
			sourceRow,
			sourceRow + count - 1,
			destinationParent,
			destinationChild
		) or destinationChild < 0 or destinationChild > self.rowCount():
			return False
		
		items: list[T] = []
		for _ in range( count ):
			items.append( self.datasource.pop( sourceRow ) )
		
		# Update destination after we removed items from the list.
		if destinationChild > sourceRow:
			destinationChild -= count
		
		for item in reversed( items ):
			self.datasource.insert( destinationChild, item )
			
		self.endMoveRows()
		
		return True
	
	
	def sort( self, column: int, order: Qt.SortOrder = Qt.SortOrder.AscendingOrder ) -> None:
		'''
		Sort items by specified field.
		'''
		
		reverse = order is not Qt.SortOrder.AscendingOrder
		key = attrgetter( self.fields[column].name )	# TODO: Fix for sub-items.
		
		self.layoutAboutToBeChanged.emit()
		self.datasource = sorted( self.datasource, key = key, reverse = reverse )
		self.layoutChanged.emit()
	
	
	def mimeTypes( self ) -> list[str]:
		'''
		Returns the list of allowed MIME types.
		'''
		
		return [ self.moveMimeType ]
	
	
	def mimeData( self, indexes: Sequence[QModelIndex] ) -> QMimeData:
		'''
		Encode a list of items into supported MIME types.
		'''
		
		mimeData = QMimeData()
		
		# Move MIME type.
		rowsData = ','.join( str( index.row() ) for index in indexes if index.column() == 0 )
		mimeData.setData( self.moveMimeType, rowsData.encode() )
		
		return mimeData
	
	
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
		
		if action is Qt.DropAction.IgnoreAction:
			return True
		
		if action is Qt.DropAction.MoveAction and data.hasFormat( self.moveMimeType ):
			sourceIndexes = [
				QPersistentModelIndex( self.index( int( sourceRow ), 0 ) )
				for sourceRow in data.data( self.moveMimeType ).toStdString().split( ',' )
			]
			targetIndex = QPersistentModelIndex( self.index( row, column ) )
			
			for sourceIndex in sourceIndexes:
				self.moveRow( QModelIndex(), sourceIndex.row(), parent, targetIndex.row() )
				
			return True
		
		return False
	
	
	def supportedDropActions( self ) -> Qt.DropAction:
		'''
		Return supported drop actions.
		'''
		
		return Qt.DropAction.MoveAction
	
	
	def supportedDragActions( self ) -> Qt.DropAction:
		'''
		Return supported drag actions.
		'''
		
		return Qt.DropAction.MoveAction