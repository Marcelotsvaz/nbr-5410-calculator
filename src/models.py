# 
# NBR 5410 Calculator
# 
# 
# Author: Marcelo Tellier Sartori Vaz <marcelotsvaz@gmail.com>



from typing import NamedTuple

from PySide6.QtCore import Qt, QAbstractTableModel, QModelIndex, QPersistentModelIndex

from installation.circuit import Circuit



# Type aliases.
ModelIndex = QModelIndex | QPersistentModelIndex



class Field( NamedTuple ):
	'''
	Field mapping for models.
	'''
	
	name: str
	editable: bool



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
			Field( 'power', True ),
			Field( 'loadType', True ),
			Field( 'voltage', True ),
			Field( 'phases', True ),
			Field( 'grouping', True ),
			Field( 'temperature', True ),
			Field( 'referenceMethod', True ),
			Field( 'wireConfiguration', True ),
			Field( 'wireType', True ),
			Field( 'length', True ),
			Field( 'wire', False ),
			Field( 'breaker', False ),
		]
		
		self.setDatasource( circuits )
	
	
	def setDatasource( self, circuits: list[Circuit] ):
		'''
		Update model's datasource.
		'''
		
		self.beginResetModel()
		self.circuits = circuits
		self.endResetModel()
	
	
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
		Return table headers.
		'''
		
		if role != Qt.DisplayRole:
			return None
		
		if orientation == Qt.Orientation.Horizontal:
			return self.fields[section].name
		
		return f'{section + 1}'
	
	
	def data( self, index: ModelIndex, role: int = 0 ) -> str | None:
		'''
		Return data for cells in table.
		'''
		
		if ( role == Qt.DisplayRole or role == Qt.EditRole ) and index.isValid():
			circuit = self.circuits[index.row()]
			field = self.fields[index.column()].name
			
			return str( getattr( circuit, field ) )
		
		return None
	
	
	def setData( self, index: ModelIndex, value: float, role: int = 0 ) -> bool:
		'''
		Update value in model.
		'''
		
		if role == Qt.EditRole and index.isValid():
			circuit = self.circuits[index.row()]
			field = self.fields[index.column()].name
			fieldType = type( getattr( circuit, field ) )
			
			try:
				setattr( circuit, field, fieldType( value ) )
				self.dataChanged.emit( index, index )
			except ValueError:
				return False
			
			return True
		
		return False