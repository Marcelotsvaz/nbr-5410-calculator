# 
# NBR 5410 Calculator
# 
# 
# Author: Marcelo Tellier Sartori Vaz <marcelotsvaz@gmail.com>



from typing import NamedTuple, Sequence, Any
from operator import attrgetter
from contextlib import suppress

from PySide6.QtCore import (
	Qt,
	QObject,
	QAbstractTableModel,
	QModelIndex,
	QPersistentModelIndex,
	QMimeData,
	Slot,
)
from PySide6.QtGui import QDrag
from PySide6.QtWidgets import QWidget, QAbstractItemView, QTableView



# Type aliases.
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



class GenericTableModel( QAbstractTableModel ):
	'''
	Maps a list of generic objects to a QTableView.
	'''
	
	def __init__(
		self,
		fields: list[Field],
		datasource: list[Any],
		parent: QObject | None = None,
	) -> None:
		super().__init__( parent )
		
		self.moveMimeType = 'application/vnd.set.row'
		
		self.fields = fields
		self.datasource = datasource
	
	
	def columnCount( self, parent: ModelIndex = QModelIndex() ) -> int:
		'''
		Return number of columns in table.
		'''
		
		_ = parent	# Unused.
		
		return len( self.fields )
	
	
	def rowCount( self, parent: ModelIndex = QModelIndex() ) -> int:
		'''
		Return number of rows in table.
		'''
		
		_ = parent	# Unused.
		
		return len( self.datasource )
	
	
	def flags( self, index: ModelIndex ) -> Qt.ItemFlag:
		'''
		Return flags for cells in table.
		'''
		
		flags = super().flags( index )
		
		if not index.isValid():
			return flags | Qt.ItemFlag.ItemIsDropEnabled
		
		if self.fields[index.column()].editable:
			flags |= Qt.ItemFlag.ItemIsEditable
		
		return flags | Qt.ItemFlag.ItemIsDragEnabled
	
	
	def headerData( self, section: int, orientation: Qt.Orientation, role: int = 0 ) -> str | None:
		'''
		Return data for table headers.
		'''
		
		role = Qt.ItemDataRole( role )
		if role is not Qt.ItemDataRole.DisplayRole:
			return None
		
		if orientation is Qt.Orientation.Horizontal:
			return self.fields[section].label
		
		return f'{section + 1}'
	
	
	def data( self, index: ModelIndex, role: int = 0 ) -> Any | None:
		'''
		Return data for table cells.
		'''
		
		role = Qt.ItemDataRole( role )
		if role not in { Qt.ItemDataRole.DisplayRole, Qt.ItemDataRole.EditRole } or not index.isValid():
			return None
		
		field = self.fields[index.column()]
		item = self.datasource[index.row()]
		
		if role is Qt.ItemDataRole.EditRole:
			return field.getFrom( item )
		
		return f'{field.getFrom( item ):{field.format}}{field.suffix}'
	
	
	def setData( self, index: ModelIndex, value: Any, role: int = 0 ) -> bool:
		'''
		Update values in model.
		'''
		
		role = Qt.ItemDataRole( role )
		if role is not Qt.ItemDataRole.EditRole or not index.isValid():
			return False
		
		field = self.fields[index.column()]
		item = self.datasource[index.row()]
		
		with suppress( ValueError ):
			field.setIn( item, value )
			self.dataChanged.emit( index, index, [ role ] )	# pyright: ignore
			
			return True
		
		return False
	
	
	def newItem( self ) -> Any:
		'''
		Return a new item to be used with `insertRows`.
		'''
		
		raise NotImplementedError()
	
	
	def insertRows( self, row: int, count: int, parent: ModelIndex = QModelIndex() ) -> bool:
		'''
		Insert new items using `newItem`.
		'''
		
		self.beginInsertRows( parent, row, row + count - 1 )
		for index in range( row, row + count ):
			self.datasource.insert( index, self.newItem() )
		self.endInsertRows()
		
		return True
	
	
	def removeRows( self, row: int, count: int, parent: ModelIndex = QModelIndex() ) -> bool:
		'''
		Delete existing items.
		'''
		
		self.beginRemoveRows( parent, row, row + count - 1 )
		for _ in range( count ):
			self.datasource.pop( row )
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
		
		items: list[Any] = []
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
		key = attrgetter( self.fields[column].name )
		
		self.layoutAboutToBeChanged.emit()	# pyright: ignore
		self.datasource = sorted( self.datasource, key = key, reverse = reverse )
		self.layoutChanged.emit()	# pyright: ignore
	
	
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
	
	
	# pylint: disable-next = useless-parent-delegation, invalid-name
	def tr( self, *args: str ) -> str:
		'''
		Translate string.
		Temporary fix for missing `tr` method in `QObject`.
		'''
		
		return super().tr( *args )	# pyright: ignore



class GenericTableView( QTableView ):
	'''
	`QTableView` for `GenericTableModel`.
	'''
	
	def __init__( self, parent: QWidget | None = None ) -> None:
		super().__init__( parent )
		
		self.setWordWrap( False )
		self.setHorizontalScrollMode( QAbstractItemView.ScrollMode.ScrollPerPixel )
		self.setAlternatingRowColors( True )
		self.horizontalHeader().setHighlightSections( False )
		self.horizontalHeader().setStretchLastSection( True )
		
		self.setSelectionBehavior( QAbstractItemView.SelectionBehavior.SelectRows )
		self.setSelectionMode( QAbstractItemView.SelectionMode.ExtendedSelection )
		
		self.setSortingEnabled( True )
		self.setDragDropMode( QAbstractItemView.DragDropMode.InternalMove )
	
	
	def startDrag( self, supportedActions: Qt.DropAction ) -> None:
		'''
		Starts a drag by calling drag.exec() using the given supportedActions.
		'''
		
		indexes = [
			index
			for index in self.selectedIndexes()
			if Qt.ItemFlag.ItemIsDragEnabled in self.model().flags( index )
		]
		
		if not indexes:
			return
		
		data = self.model().mimeData( indexes )
		
		drag = QDrag( self )
		drag.setMimeData( data )
		drag.exec( supportedActions )
	
	
	@Slot()
	def newItem( self ) -> None:
		'''
		Insert new item at end of table.
		'''
		
		itemCount = self.model().rowCount()
		self.model().insertRow( itemCount )
	
	
	@Slot()
	def deleteSelectedItems( self ) -> None:
		'''
		Delete selected items from table.
		'''
		
		indexes = {
			QPersistentModelIndex( index )
			for index in self.selectedIndexes()
			if index.column() == 0
		}
		
		for index in indexes:
			self.model().removeRow( index.row() )