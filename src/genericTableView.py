# 
# NBR 5410 Calculator
# 
# 
# Author: Marcelo Tellier Sartori Vaz <marcelotsvaz@gmail.com>



from typing import NamedTuple, Any
from operator import attrgetter
from contextlib import suppress

from PySide6.QtCore import (
	Qt,
	QObject,
	QAbstractTableModel,
	QModelIndex,
	QPersistentModelIndex,
	Slot,
)
from PySide6.QtWidgets import QTableView



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
		datasource: list[Any] | None = None,
		parent: QObject | None = None,
	) -> None:
		'''
		Setup fields and load initial data.
		'''
		
		super().__init__( parent )
		
		self.fields = fields
		self.datasource = datasource or []
	
	
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
			return flags
		
		if self.fields[index.column()].editable:
			flags |= Qt.ItemFlag.ItemIsEditable
		
		return flags
	
	
	def headerData( self, section: int, orientation: Qt.Orientation, role: int = 0 ) -> str | None:
		'''
		Return data for table headers.
		'''
		
		if role != Qt.ItemDataRole.DisplayRole:
			return None
		
		if orientation == Qt.Orientation.Horizontal:
			return self.fields[section].label
		
		return f'{section + 1}'
	
	
	def data( self, index: ModelIndex, role: int = 0 ) -> Any | None:
		'''
		Return data for table cells.
		'''
		
		if role not in { Qt.ItemDataRole.DisplayRole, Qt.ItemDataRole.EditRole } or not index.isValid():
			return None
		
		field = self.fields[index.column()]
		item = self.datasource[index.row()]
		
		if role == Qt.ItemDataRole.EditRole:
			return field.getFrom( item )
		
		return f'{field.getFrom( item ):{field.format}}{field.suffix}'
	
	
	def setData( self, index: ModelIndex, value: Any, role: int = 0 ) -> bool:
		'''
		Update values in model.
		'''
		
		if role != Qt.ItemDataRole.EditRole or not index.isValid():
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
		Insert new item using `newItem`.
		'''
		
		self.beginInsertRows( parent, row, row + count - 1 )
		for index in range( row, row + count ):
			self.datasource.insert( index, self.newItem() )
		self.endInsertRows()
		
		return True
	
	
	def removeRows( self, row: int, count: int, parent: ModelIndex = QModelIndex() ) -> bool:
		'''
		Delete existing item.
		'''
		
		self.beginRemoveRows( parent, row, row + count - 1 )
		for _ in range( count ):
			self.datasource.pop( row )
		self.endRemoveRows()
		
		return True
	
	
	def sort( self, column: int, order: Qt.SortOrder = Qt.SortOrder.AscendingOrder ) -> None:
		'''
		Sort items by specified field.
		'''
		
		reverse = order != Qt.SortOrder.AscendingOrder
		key = attrgetter( self.fields[column].name )
		
		self.layoutAboutToBeChanged.emit()	# pyright: ignore
		self.datasource = sorted( self.datasource, key = key, reverse = reverse )
		self.layoutChanged.emit()	# pyright: ignore
	
	
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
	
	@Slot()
	def newItem( self ) -> None:
		'''
		Insert new item at end of table.
		'''
		
		itemCount = self.model().rowCount()
		self.model().insertRow( itemCount )
	
	
	@Slot()
	def deleteItem( self ) -> None:
		'''
		Delete selected item from table.
		'''
		
		if indexes := self.selectedIndexes():
			self.model().removeRow( indexes[0].row() )