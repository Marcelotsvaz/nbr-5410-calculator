'''
Partial implementation of `QAbstractItemModel`.
'''

from collections.abc import Iterable, Sequence
from contextlib import suppress
from typing import Any, cast, overload, override

from PySide6.QtCore import (
	QAbstractItemModel,
	QMimeData,
	QModelIndex,
	QObject,
	QPersistentModelIndex,
	Qt,
)
from pydantic import TypeAdapter

from nbr_5410_calculator.generic_model_views.items import GenericItem, ItemFieldInfo, RootItem



type ModelIndex = QModelIndex | QPersistentModelIndex



class GenericItemModel[ItemT: GenericItem]( QAbstractItemModel ):
	'''
	Maps a list of generic objects to a `QAbstractItemView`.
	'''
	
	jsonMimeType = 'application/json'
	
	
	@override
	def __init__(
		self,
		datasource: list[ItemT],
		dataType: type[ItemT],
		parent: QObject | None = None,
	) -> None:
		super().__init__( parent )
		
		self.root = RootItem( items = datasource )
		self.dataType = dataType
		self.updateFieldOrder()
	
	
	def updateFieldOrder( self, fieldOrder: Iterable[str] | None = None ) -> None:
		'''
		Update which fields are displayed and in which order.
		'''
		
		itemFields = self.dataType.__getItemFields__()
		
		if fieldOrder is None:
			fieldOrder = sorted( itemFields.keys() )
		
		self.fields: list[ItemFieldInfo] = []
		for name in fieldOrder:
			if name not in itemFields:
				raise ValueError( f'No definition for field `{name}` in class {self.dataType}.' )
			
			self.fields.append( ItemFieldInfo.fromItemFieldList( name, itemFields[name] ) )
	
	
	def itemFromIndex( self, index: ModelIndex ) -> ItemT:
		'''
		Return the item associated with the given `index`.
		'''
		
		if item := cast( ItemT | None, index.internalPointer() ):
			return item
		
		raise LookupError( 'Index points to `None`.' )
	
	
	@override
	def index( self, row: int, column: int, parent: ModelIndex = QModelIndex() ) -> QModelIndex:
		'''
		Return the index of the item in the model specified by the given `row`, `column` and
		`parent` index.
		'''
		
		# Root index.
		if not parent.isValid() and row == 0:
			return self.createIndex( row, column, self.root )
		
		children = self.itemFromIndex( parent ).children
		
		if not children or not 0 <= row < len( children ):
			raise ValueError( 'Row not in parent or parent does not support children.' )
		
		return self.createIndex( row, column, children[row] )
	
	
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
		
		
		# Iterate all children recursively.
		parents: list[tuple[int, GenericItem]] = [ ( 0, self.root ) ]
		while parents:
			parentIndex, parent = parents.pop()
			
			if not parent.children:
				continue
			
			if self.itemFromIndex( child ) in parent.children:
				return self.createIndex( parentIndex, 0, parent )
			
			parents += enumerate( parent.children )
		
		if self.itemFromIndex( child ) is self.root:
			return QModelIndex()
		
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
		
		if not parent.isValid():
			raise ValueError( 'Invalid parent index.' )
		
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
		
		field = self.fields[index.column()]
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
		
		field = self.fields[section]
		assert field is not None
		
		return field.label
	
	
	@override
	def data( self, index: ModelIndex, role: int = 0 ) -> Any | None:
		'''
		Return data for table cells.
		'''
		
		role = Qt.ItemDataRole( role )
		if role not in { Qt.ItemDataRole.DisplayRole, Qt.ItemDataRole.EditRole }:
			return None
		
		field = self.fields[index.column()]
		item = self.itemFromIndex( index )
		
		# This column is only valid for a parent or child of this item.
		if not field:
			return None
		
		# Edit role.
		if role is Qt.ItemDataRole.EditRole:
			return field.valueForEdition( item )
		
		# Display role.
		return field.valueForDisplay( item )
	
	
	@override
	def setData( self, index: ModelIndex, value: Any, role: int = 0 ) -> bool:
		'''
		Update values in model.
		'''
		
		role = Qt.ItemDataRole( role )
		if role is not Qt.ItemDataRole.EditRole or not index.isValid():
			return False
		
		field = self.fields[index.column()]
		item = self.itemFromIndex( index )
		assert field is not None
		
		with suppress( ValueError ):
			field.setValue( item, value )
			self.dataChanged.emit( index, index, [ role ] )
			
			return True
		
		return False
	
	
	def insertItem( self, item: ItemT, row: int = -1, parent: ModelIndex = QModelIndex() ) -> None:
		'''
		Insert an existing item into the model's datasource.
		'''
		
		children = self.itemFromIndex( parent ).children
		
		if children is None:
			raise ValueError( 'Parent does not support children.' )
		
		if row < 0:
			row = len( children ) + 1 + row
		
		self.beginInsertRows( parent, row, row )
		children.insert( row, item )
		self.endInsertRows()
	
	
	@override
	def removeRows( self, row: int, count: int, parent: ModelIndex = QModelIndex() ) -> bool:
		'''
		Delete existing items.
		'''
		
		children = self.itemFromIndex( parent ).children
		
		if children is None:
			raise ValueError( 'Parent does not support children.' )
		
		self.beginRemoveRows( parent, row, row + count - 1 )
		for _ in range( count ):
			children.pop( row )
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
		
		sourceChildren = self.itemFromIndex( sourceParent ).children
		destinationChildren = self.itemFromIndex( destinationParent ).children
		
		if sourceChildren is None or destinationChildren is None:
			raise ValueError( 'Parent does not support children.' )
		
		items: list[ItemT] = []
		for _ in range( count ):
			items.append( sourceChildren.pop( sourceRow ) )
		
		# Update destination after we removed items from the list.
		if destinationParent == sourceParent and destinationChild >= sourceRow:
			destinationChild -= count
		
		for item in reversed( items ):
			destinationChildren.insert( destinationChild, item )
		
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
		
		_ = column	# Unused.
		
		match action:
			case Qt.DropAction.IgnoreAction:
				return True
			
			case Qt.DropAction.MoveAction | Qt.DropAction.CopyAction if data.hasFormat( self.jsonMimeType ):
				jsonBytes = data.data( self.jsonMimeType ).data()
				items = TypeAdapter( list[ItemT] ).validate_json( bytes( jsonBytes ) )
				
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