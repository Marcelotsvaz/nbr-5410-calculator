'''
Partial implementation of `QAbstractItemModel`.
'''

from collections.abc import Mapping, Sequence
from functools import cache
from typing import Any, cast, overload, override

from PySide6.QtCore import (
	QAbstractItemModel,
	QMimeData,
	QModelIndex,
	QObject,
	QPersistentModelIndex,
	Qt,
)
from pydantic import TypeAdapter, ValidationError

from nbr_5410_calculator.generic_model_views.items import GenericItem, ItemFieldInfo, RootItem



type ModelIndex = QModelIndex | QPersistentModelIndex
type FieldOrder[T] = Mapping[type[T], Sequence[str | None]]



class GenericItemModel[ItemT: GenericItem]( QAbstractItemModel ):
	'''
	Maps a list of generic objects to a `QAbstractItemView`.
	'''
	
	jsonMimeType = 'application/json'
	
	
	@override
	def __init__(
		self,
		datasource: list[ItemT],
		dataTypes: list[type[ItemT]],
		parent: QObject | None = None,
	) -> None:
		super().__init__( parent )
		
		self.root = RootItem( childrenType = dataTypes[0], items = [] )
		self.root.items = datasource	# TODO: Don't copy list in constructor.
		self.dataTypes = dataTypes
		self.updateFieldOrder()
	
	
	def updateFieldOrder( self, fieldOrder: FieldOrder[ItemT] | None = None ) -> None:
		'''
		Update which fields are displayed and in which order.
		'''
		
		if fieldOrder is None:
			fieldOrder = {}
		
		self.fields: dict[type[ItemT], list[ItemFieldInfo | None]] = {}
		for dataType in self.dataTypes:
			itemFields = dataType.__getItemFields__()
			
			self.fields[dataType] = []
			for name in fieldOrder.get( dataType, sorted( itemFields.keys() ) ):
				if not name:
					self.fields[dataType].append( None )
					continue
				
				if name not in itemFields:
					raise ValueError( f'No definition for field `{name}` in class {dataType}.' )
				
				self.fields[dataType].append( ItemFieldInfo.fromItemFieldList( name, itemFields[name] ) )
	
	
	def itemFromIndex( self, index: ModelIndex ) -> ItemT:
		'''
		Return the item associated with the given `index`.
		'''
		
		if item := cast( ItemT | None, index.internalPointer() ):
			return item
		
		raise LookupError( 'Index points to `None`.' )
	
	
	def fieldFromIndex( self, index: ModelIndex ) -> ItemFieldInfo | None:
		'''
		Return the `ItemFieldInfo` instance associated with the given `index`.
		'''
		
		item = self.itemFromIndex( index )
		
		for rowType, fields in self.fields.items():
			if isinstance( item, rowType ):
				return fields[index.column()]
		
		raise TypeError( f'No field for type `{type( item )}`.' )
	
	
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
		
		return len( self.fields[self.dataTypes[0]] )
	
	
	@override
	def rowCount( self, parent: ModelIndex = QModelIndex() ) -> int:
		'''
		Return the number of rows under the given `parent`.
		An invalid `parent` returns the number of top-level rows.
		'''
		
		assert parent.isValid()
		
		return len( self.itemFromIndex( parent ).children )
	
	
	@override
	def flags( self, index: ModelIndex ) -> Qt.ItemFlag:
		'''
		Return flags for cells in table.
		'''
		
		flags = super().flags( index )
		
		# TODO: Filter here on top of canDropMimeData?
		flags |= Qt.ItemFlag.ItemIsDropEnabled
		
		if self.itemFromIndex( index ) is self.root:
			return flags
		
		field = self.fieldFromIndex( index )
		if field and field.editable:
			flags |= Qt.ItemFlag.ItemIsEditable
		
		if self.dragActionsForIndex( index ):
			flags |= Qt.ItemFlag.ItemIsDragEnabled
		
		return flags
	
	
	@override
	def headerData( self, section: int, orientation: Qt.Orientation, role: int = 0 ) -> str | None:
		'''
		Return data for table headers.
		'''
		
		if orientation is Qt.Orientation.Vertical:
			return f'{section + 1}'
		
		field = self.fields[self.dataTypes[0]][section]
		assert field is not None
		
		match Qt.ItemDataRole( role ):
			case Qt.ItemDataRole.DisplayRole:
				return field.label
			
			case Qt.ItemDataRole.ToolTipRole:
				return field.description
			
			case _:
				return None
	
	
	@override
	def data( self, index: ModelIndex, role: int = 0 ) -> Any | None:
		'''
		Return data for table cells.
		'''
		
		try:
			field = self.fieldFromIndex( index )
		except TypeError:
			return None
		
		item = self.itemFromIndex( index )
		
		match Qt.ItemDataRole( role ):
			# This column is only valid for a parent or child of this item.
			case _ if not field:
				return None
			
			case Qt.ItemDataRole.DisplayRole:
				return field.valueForDisplay( item )
			
			case Qt.ItemDataRole.EditRole:
				return field.valueForEdition( item )
			
			case _:
				return None
	
	
	@override
	def setData( self, index: ModelIndex, value: Any, role: int = 0 ) -> bool:
		'''
		Update values in model.
		'''
		
		role = Qt.ItemDataRole( role )
		
		if role is not Qt.ItemDataRole.EditRole:
			return False
		
		field = self.fieldFromIndex( index )
		item = self.itemFromIndex( index )
		assert field is not None
		
		try:
			field.setValue( item, value )
			self.dataChanged.emit( index, index, [ role ] )
			return True
		except ValidationError:
			return False
	
	
	def insertItem( self, item: ItemT, row: int = -1, parent: ModelIndex | None = None ) -> None:
		'''
		Insert an existing item into the model's datasource.
		'''
		
		if parent is None:
			parent = self.index( 0, 0 )
		
		parentItem = self.itemFromIndex( parent )
		
		if not parentItem.isChildValid( item ):
			raise ValueError( '`Item` is not a valid child or parent does not support children.' )
		
		if row < 0:
			row = len( parentItem.children ) + 1 + row
		
		self.beginInsertRows( parent, row, row )
		parentItem.insertChild( row, item )
		self.endInsertRows()
	
	
	@override
	def removeRows( self, row: int, count: int, parent: ModelIndex = QModelIndex() ) -> bool:
		'''
		Delete existing items.
		'''
		
		parentItem = self.itemFromIndex( parent )
		
		self.beginRemoveRows( parent, row, row + count - 1 )
		for _ in range( count ):
			item = parentItem.children[row]
			parentItem.removeChild( row, item )
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
		
		sourceParentItem = self.itemFromIndex( sourceParent )
		items: list[ItemT] = []
		for _ in range( count ):
			items.append( sourceParentItem.children.pop( sourceRow ) )
		
		# Update destination after we removed items from the list.
		if destinationParent == sourceParent and destinationChild >= sourceRow:
			destinationChild -= count
		
		destinationParentItem = self.itemFromIndex( destinationParent )
		for item in reversed( items ):
			if not destinationParentItem.isChildValid( item ):
				raise ValueError( 'Source item is not a valid children of destination.' )
			destinationParentItem.children.insert( destinationChild, item )
		
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
	
	
	def dragActionsForIndex( self, sourceIndex: ModelIndex ) -> Qt.DropAction:
		'''
		Return drag actions supported by `sourceIndex`.
		TODO: Item instead of index?
		'''
		
		return Qt.DropAction.IgnoreAction
	
	
	@override
	def supportedDragActions( self ) -> Qt.DropAction:
		'''
		Return supported drag actions.
		TODO: Choose default.
		'''
		
		return Qt.DropAction.MoveAction
	
	
	@override
	def supportedDropActions( self ) -> Qt.DropAction:
		'''
		Return supported drop actions.
		TODO: Choose default.
		'''
		
		return Qt.DropAction.MoveAction
	
	
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
	
	
	@cache	# TODO
	def itemsFromMimeData( self, mimeData: QMimeData ) -> list[ItemT]:
		'''
		Parse `QMimeData` using default MIME type.
		'''
		
		jsonBytes = mimeData.data( self.jsonMimeType ).data()
		
		return TypeAdapter( list[ItemT] ).validate_json( bytes( jsonBytes ) )
	
	
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
				items = self.itemsFromMimeData( data )
				
				for item in reversed( items ):
					self.insertItem( item, row, parent )
				
				return True
			
			case _:
				return False
	
	
	@override
	def canDropMimeData(
		self,
		data: QMimeData,
		action: Qt.DropAction,
		row: int,
		column: int,
		parent: ModelIndex,
	) -> bool:
		parentItem = self.itemFromIndex( parent )
		
		return all( parentItem.isChildValid( item ) for item in self.itemsFromMimeData( data ) )