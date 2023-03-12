# 
# NBR 5410 Calculator
# 
# 
# Author: Marcelo Tellier Sartori Vaz <marcelotsvaz@gmail.com>



from PySide6.QtCore import QObject

from genericTreeView import Field, GenericModel
from installation.conduitRun import ConduitRun



class ConduitRunsModel( GenericModel ):
	'''
	Map a list of `ConduitRun`s to a QTableView.
	'''
	
	def __init__( self, conduitRuns: list[ConduitRun], parent: QObject | None = None ) -> None:
		fields = [
			Field( 'name',		self.tr('Name') ),
			Field( 'diameter',	self.tr('Diameter'),	format = ',', suffix = ' mm' ),
			Field( 'length',	self.tr('Length'),		format = ',', suffix = ' m' ),
		]
		
		super().__init__( fields, conduitRuns, parent = parent )
	
	
	def newItem( self ) -> ConduitRun:
		'''
		Return a new `ConduitRun` to be used with `insertRows`.
		'''
		
		conduitRun = ConduitRun(
			name = self.tr('New Conduit Run'),
			diameter = 25.0,
			length = 10.0,
		)
		
		return conduitRun