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
from PySide6.QtWidgets import QWidget, QTableView

from installation.circuit import (
	LoadType,
	WireMaterial,
	WireInsulation,
	WireType,
	ReferenceMethod,
	WireConfiguration,
	Circuit,
)



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



class CircuitsModel( QAbstractTableModel ):
	'''
	Maps a `Circuit` object to a QTableView.
	'''
	
	def __init__( self, parent: QObject | None = None, circuits: list[Circuit] | None = None ) -> None:
		'''
		Setup fields and load initial data.
		'''
		
		super().__init__( parent )
		
		self.fields = [
			Field( 'name',						self.tr('Name') ),
			Field( 'power',						self.tr('Power'),			format = ',', suffix = ' VA' ),
			Field( 'loadType.value',			self.tr('Load Type'),		setter = 'loadType' ),
			Field( 'voltage',					self.tr('Voltage'),			format = ',', suffix = ' V' ),
			Field( 'phases',					self.tr('Phases') ),
			Field( 'grouping',					self.tr('Grouping') ),
			Field( 'temperature',				self.tr('Temperature'),		suffix = '°C' ),
			Field( 'referenceMethod.name',		self.tr('Ref. Method'),		setter = 'referenceMethod' ),
			Field( 'wireConfiguration.value',	self.tr('Configuration'),	setter = 'wireConfiguration' ),
			Field( 'wireType',					self.tr('Wire Type') ),
			Field( 'length',					self.tr('Length'),			format = ',', suffix = ' m' ),
			Field( 'current',					self.tr('Current'),			False, format = ',.1f', suffix = ' A' ),
			Field( 'breaker.current',			self.tr('Breaker'),			False, suffix = ' A' ),
			Field( 'wire.capacity',				self.tr('Wire Capacity'),	False, format = ',.1f', suffix = ' A' ),
			Field( 'wire.section',				self.tr('Wire Section'),	False, format = ',', suffix = ' mm²' ),
		]
		
		self.circuits = circuits or []
	
	
	# pylint: disable-next = useless-parent-delegation, invalid-name
	def tr( self, *args: str ) -> str:
		'''
		Translate string.
		Temporary fix for missing `tr` method in `QObject`.
		'''
		
		return super().tr( *args )	# pyright: ignore
	
	
	def rowCount( self, parent: ModelIndex = QModelIndex() ) -> int:
		'''
		Return number of rows in table.
		'''
		
		_ = parent	# Unused.
		
		return len( self.circuits )
	
	
	def columnCount( self, parent: ModelIndex = QModelIndex() ) -> int:
		'''
		Return number of columns in table.
		'''
		
		_ = parent	# Unused.
		
		return len( self.fields )
	
	
	def flags( self, index: ModelIndex ) -> Qt.ItemFlag:
		'''
		Return flags for cells in table.
		'''
		
		flags = super().flags( index )
		
		if not index.isValid():
			return flags
		
		if self.fields[index.column()].editable:
			return flags | Qt.ItemFlag.ItemIsEditable
		
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
		
		if role in { Qt.ItemDataRole.DisplayRole, Qt.ItemDataRole.EditRole } and index.isValid():
			field = self.fields[index.column()]
			circuit = self.circuits[index.row()]
			
			if role == Qt.ItemDataRole.EditRole:
				return field.getFrom( circuit )
			
			return f'{field.getFrom( circuit ):{field.format}}{field.suffix}'
		
		return None
	
	
	def setData( self, index: ModelIndex, value: Any, role: int = 0 ) -> bool:
		'''
		Update values in model.
		'''
		
		if role == Qt.ItemDataRole.EditRole and index.isValid():
			field = self.fields[index.column()]
			circuit = self.circuits[index.row()]
			
			with suppress( ValueError ):
				field.setIn( circuit, value )
				self.dataChanged.emit( index, index, role )	# pyright: ignore
				
				return True
		
		return False
	
	
	def insertRows( self, row: int, count: int, parent: ModelIndex = QModelIndex() ) -> bool:
		'''
		Create new `Circuit`s.
		'''
		
		self.beginInsertRows( parent, row, row + count - 1 )
		
		for index in range( row, row + count ):
			wireType = WireType( WireMaterial.COPPER, WireInsulation.PVC )
			circuit = Circuit(
				name				= self.tr('New Circuit'),
				loadType			= LoadType.POWER,
				voltage				= 127,
				phases				= 1,
				grouping			= 1,
				length				= 10.0,
				referenceMethod		= ReferenceMethod.B1,
				wireConfiguration	= WireConfiguration.TWO,
				wireType			= wireType,
				temperature			= 30,
				power				= 1000,
			)
			self.circuits.insert( index, circuit )
		
		self.endInsertRows()
		
		return True
	
	
	def removeRows( self, row: int, count: int, parent: ModelIndex = QModelIndex() ) -> bool:
		'''
		Delete existing `Circuit`s.
		'''
		
		self.beginRemoveRows( parent, row, row + count - 1 )
		for _ in range( count ):
			self.circuits.pop( row )
		self.endRemoveRows()
		
		return True
	
	
	def sort( self, column: int, order: Qt.SortOrder = Qt.SortOrder.AscendingOrder ) -> None:
		'''
		Sort `Circuit`s by specified field.
		'''
		
		reverse = order == Qt.SortOrder.DescendingOrder
		key = attrgetter( self.fields[column].name )
		
		self.layoutAboutToBeChanged.emit()	# pyright: ignore
		self.circuits = sorted( self.circuits, key = key, reverse = reverse )
		self.layoutChanged.emit()	# pyright: ignore



class CircuitsTableView( QTableView ):
	'''
	`QTableView` for `CircuitsModel`.
	'''
	
	def __init__( self, parent: QWidget | None ) -> None:
		'''
		Initialize with empty `CircuitsModel`.
		'''
		
		super().__init__( parent )
		self.setDatasource( [] )
	
	
	def setDatasource( self, circuits: list[Circuit] ) -> None:
		'''
		Create new `CircuitsModel` from `circuits` and assign it to this view. 
		'''
		
		self.setModel( CircuitsModel( self, circuits ) )
	
	
	@Slot()
	def newCircuit( self ) -> None:
		'''
		Insert new `Circuit` at end of table.
		'''
		
		circuitCount = self.model().rowCount()
		self.model().insertRow( circuitCount )
	
	
	@Slot()
	def deleteCircuit( self ) -> None:
		'''
		Remove selected `Circuit` from table.
		'''
		
		if indexes := self.selectedIndexes():
			self.model().removeRow( indexes[0].row() )