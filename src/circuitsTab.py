# 
# NBR 5410 Calculator
# 
# 
# Author: Marcelo Tellier Sartori Vaz <marcelotsvaz@gmail.com>



from typing import NamedTuple
from operator import attrgetter

from PySide6.QtCore import Qt, QAbstractTableModel, QModelIndex, QPersistentModelIndex, Slot
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
	editable: bool
	format: str = ''
	suffix: str = ''



class CircuitModel( QAbstractTableModel ):
	'''
	Maps a `Circuit` object to a QTableView.
	'''
	
	def __init__( self, circuits: list[Circuit] ) -> None:
		'''
		Setup fields and load initial data.
		'''
		
		super().__init__()
		
		self.fields = [
			Field( 'name', True ),
			Field( 'power', True, format = ',', suffix = ' VA' ),
			Field( 'loadType.value', True ),
			Field( 'voltage', True, format = ',', suffix = ' V' ),
			Field( 'phases', True ),
			Field( 'grouping', True ),
			Field( 'temperature', True, suffix = '°C' ),
			Field( 'referenceMethod.name', True ),
			Field( 'wireConfiguration.value', True ),
			Field( 'wireType', True ),
			Field( 'length', True, format = ',', suffix = ' m' ),
			Field( 'current', False, format = ',.1f', suffix = ' A' ),
			Field( 'breaker.current', False, suffix = ' A' ),
			Field( 'wire.capacity', False, format = ',.1f', suffix = ' A' ),
			Field( 'wire.section', False, format = ',', suffix = ' mm²' ),
		]
		
		self.circuits = circuits
	
	
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
			return self.fields[section].name
		
		return f'{section + 1}'
	
	
	def data( self, index: ModelIndex, role: int = 0 ) -> str | None:
		'''
		Return data for table cells.
		'''
		
		if role in { Qt.ItemDataRole.DisplayRole, Qt.ItemDataRole.EditRole } and index.isValid():
			circuit = self.circuits[index.row()]
			fieldGetter = attrgetter( self.fields[index.column()].name )
			fieldFormat = self.fields[index.column()].format
			fieldSuffix = self.fields[index.column()].suffix
			
			if role == Qt.ItemDataRole.EditRole:
				return str( fieldGetter( circuit ) )
			
			return f'{fieldGetter( circuit ):{fieldFormat}}{fieldSuffix}'
		
		return None
	
	
	def setData( self, index: ModelIndex, value: float, role: int = 0 ) -> bool:
		'''
		Update values in model.
		'''
		
		if role == Qt.ItemDataRole.EditRole and index.isValid():
			circuit = self.circuits[index.row()]
			field = self.fields[index.column()].name
			fieldType = type( getattr( circuit, field ) )
			
			try:
				setattr( circuit, field, fieldType( value ) )
				# pylint: disable-next=line-too-long
				self.dataChanged.emit( index, index, role )	# pyright: ignore [reportGeneralTypeIssues, reportUnknownMemberType]
			except ValueError:
				return False
			
			return True
		
		return False
	
	
	def insertRows( self, row: int, count: int, parent: ModelIndex = QModelIndex() ) -> bool:
		'''
		Create new `Circuit`s.
		'''
		
		self.beginInsertRows( parent, row, row + count - 1 )
		
		wireType = WireType( WireMaterial.COPPER, WireInsulation.PVC )
		circuit = Circuit(
			name				= 'New Circuit',
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
		
		for index in range( row, row + count ):
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



class CircuitsTableView( QTableView ):
	'''
	`QTableView` for `CircuitModel`.
	'''
	
	def __init__( self, parent: QWidget | None ) -> None:
		'''
		Initialize with empty `CircuitModel`.
		'''
		
		super().__init__( parent )
		self.setDatasource( [] )
	
	
	def setDatasource( self, circuits: list[Circuit] ) -> None:
		'''
		Create new `CircuitModel` from `circuits` and assign it to this view. 
		'''
		
		self.setModel( CircuitModel( circuits ) )
	
	
	@Slot()
	def newCircuit( self ) -> None:
		'''
		Insert new `Circuit` at end of table.
		'''
		
		circuitCount = self.model().rowCount()
		self.model().insertRow( circuitCount )