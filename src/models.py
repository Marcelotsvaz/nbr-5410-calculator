# 
# NBR 5410 Calculator
# 
# 
# Author: Marcelo Tellier Sartori Vaz <marcelotsvaz@gmail.com>



from PySide6.QtCore import Qt, QAbstractTableModel, QModelIndex, QPersistentModelIndex

from installation.circuit import Circuit



# Type aliases.
ModelIndex = QModelIndex | QPersistentModelIndex



class CircuitModel( QAbstractTableModel ):
	'''
	Maps a `Circuit` object to a QTableView.
	'''
	
	def __init__( self, circuits: list[Circuit] ) -> None:
		'''
		Setup fields and load initial data.
		'''
		
		super().__init__()
		
		self.circuits = circuits
		self.fields = [
			'name',
			'power',
			'loadType',
			'voltage',
			'phases',
			'grouping',
			'temperature',
			'referenceMethod',
			'wireConfiguration',
			'wireType',
			'length',
		]
	
	
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
	
	
	def headerData( self, section: int, orientation: Qt.Orientation, role: int = 0 ) -> str | None:
		'''
		Return table headers.
		'''
		
		if role != Qt.DisplayRole:
			return None
		
		if orientation == Qt.Orientation.Horizontal:
			return self.fields[section]
		
		return f'{section}'
	
	
	def data( self, index: ModelIndex, role: int = 0 ) -> str | None:
		'''
		Return data for cells in table.
		'''
		
		if role == Qt.DisplayRole:
			circuit = self.circuits[index.row()]
			field = self.fields[index.column()]
			
			return str( getattr( circuit, field ) )
		
		return None