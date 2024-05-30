'''
Partial implementation of `QAbstractItemModel`.
'''

from collections.abc import Sequence
from contextlib import suppress
from enum import Enum
from operator import attrgetter
from typing import Self, NamedTuple, Any, cast, overload, override

from PySide6.QtCore import (
	QAbstractItemModel,
	QMimeData,
	QModelIndex,
	QObject,
	QPersistentModelIndex,
	Qt,
)
from pydantic import BaseModel, TypeAdapter



type ModelIndex = QModelIndex | QPersistentModelIndex



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



class GenericItem( BaseModel ):
	'''
	TODO
	'''
	
	@property
	def children( self ) -> list[Self] | None:
		'''
		TODO
		'''
		
		return None



class GenericItemModel[ItemT: GenericItem]( QAbstractItemModel ):
	'''
	Maps a list of generic objects to a `QAbstractItemView`.
	'''
	
	jsonMimeType = 'application/json'
	
	
	@override
	def __init__(
		self,
		fields: list[Field] | list[Field | None],
		datasource: list[ItemT],
		childFields: list[Field] | list[Field | None] | None = None,
		parent: QObject | None = None,
	) -> None:
		super().__init__( parent )
		
		self.fields = fields
		self.datasource = datasource
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
	
	
	def itemFromIndex( self, index: ModelIndex ) -> ItemT:
		'''
		Return the item associated with the given `index`.
		'''
		
		return cast( ItemT, index.internalPointer() )
	
	
	@override
	def index( self, row: int, column: int, parent: ModelIndex = QModelIndex() ) -> QModelIndex:
		'''
		Return the index of the item in the model specified by the given `row`, `column` and
		`parent` index.
		'''
		
		# Top-level item.
		if not parent.isValid():
			if not 0 <= row < len( self.datasource ):
				# Requested row not in datasource.
				return QModelIndex()
			
			return self.createIndex( row, column, self.datasource[row] )
		
		# Sub-item.
		parentItem = self.itemFromIndex( parent )
		
		if not parentItem.children:
			return QModelIndex()
		
		if not 0 <= row < len( parentItem.children ):
			# Requested row not in datasource.
			return QModelIndex()
		
		return self.createIndex( row, column, parentItem.children[row] )
	
	
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
		
		childItem = self.itemFromIndex( child )
		
		if childItem in self.datasource:
			# Top-level items have no parent.
			return QModelIndex()
		
		# Iterate all children recursively.
		parents = list( enumerate( self.datasource[:] ) )
		while parents:
			parentIndex, parent = parents.pop()
			
			if not parent.children:
				continue
			
			if childItem in parent.children:
				return self.createIndex( parentIndex, 0, parent )
			
			parents += enumerate( parent.children )
		
		raise LookupError( 'Could not find child in datasource hierarchy.' )
	
	
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
		
		if children := self.itemFromIndex( parent ).children:
			return len( children )
		
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
		
		if self.itemFromIndex( index ).children is not None:
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
	
	
	def insertItem( self, item: ItemT, row: int = -1, parent: ModelIndex = QModelIndex() ) -> None:
		'''
		Insert an existing item into the model's datasource.
		'''
		
		if parent.isValid():
			datasource = self.itemFromIndex( parent ).children
			
			if datasource is None:
				raise ValueError( 'Parent does not support children.' )
		else:
			datasource = self.datasource
		
		if row < 0:
			row = len( datasource ) + 2 + row
		
		self.beginInsertRows( parent, row, row )
		datasource.insert( row, item )
		self.endInsertRows()
	
	
	@override
	def removeRows( self, row: int, count: int, parent: ModelIndex = QModelIndex() ) -> bool:
		'''
		Delete existing items.
		'''
		
		if parent.isValid():
			datasource = self.itemFromIndex( parent ).children
			
			if datasource is None:
				raise ValueError( 'Parent does not support children.' )
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
			sourceDatasource = self.itemFromIndex( sourceParent ).children
		else:
			sourceDatasource = self.datasource
		
		if destinationParent.isValid():
			destinationDatasource = self.itemFromIndex( destinationParent ).children
		else:
			destinationDatasource = self.datasource
		
		if sourceDatasource is None or destinationDatasource is None:
			raise ValueError( 'Parent does not support children.' )
		
		items: list[ItemT] = []
		for _ in range( count ):
			items.append( sourceDatasource.pop( sourceRow ) )
		
		# Update destination after we removed items from the list.
		if destinationParent == sourceParent and destinationChild >= sourceRow:
			destinationChild -= count
		
		for item in reversed( items ):
			destinationDatasource.insert( destinationChild, item )
		
		self.endMoveRows()
		
		return True
	
	
	# @override
	# def sort( self, column: int, order: Qt.SortOrder = Qt.SortOrder.AscendingOrder ) -> None:
	# 	'''
	# 	Sort items by specified field.
	# 	'''
		
	# 	reverse = order is not Qt.SortOrder.AscendingOrder
	# 	key = attrgetter( self.fields[column].name )	# TODO: Fix for sub-items.
		
	# 	self.layoutAboutToBeChanged.emit()
	# 	# TODO: Remember the QModelIndex that will change https://doc.qt.io/qtforpython-6/PySide6/QtCore/QAbstractItemModel.html#PySide6.QtCore.QAbstractItemModel.layoutChanged
	# 	self.datasource = sorted( self.datasource, key = key, reverse = reverse )
	# 	# TODO: Call changePersistentIndex()
	# 	self.layoutChanged.emit()
	
	
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
		
		jsonBytes = TypeAdapter( list[ItemT] ).dump_json( items )
		
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
				items = TypeAdapter( list[ItemT] ).validate_json( jsonBytes )
				
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