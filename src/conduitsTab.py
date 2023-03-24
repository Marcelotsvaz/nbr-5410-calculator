# 
# NBR 5410 Calculator
# 
# 
# Author: Marcelo Tellier Sartori Vaz <marcelotsvaz@gmail.com>



from PySide6.QtCore import QObject

from genericModelViews.models import Field, GenericItemModel
from installation.conduitRun import ConduitRun



class ConduitRunsModel( GenericItemModel[ConduitRun] ):
	'''
	Map a list of `ConduitRun`s to a QTableView.
	'''
	
	def __init__( self, conduitRuns: list[ConduitRun], parent: QObject | None = None ) -> None:
		fields = [
			Field( 'name',						self.tr('Name') ),
			Field( 'length',					self.tr('Length'),				format = ',', suffix = ' m' ),
			Field( 'conduit.nominalDiameter',	self.tr('Diameter'),	False ),
			Field( 'fillFactor',				self.tr('Fill Factor'),	False,	format = '.1%' ),
		]
		childListName = 'circuits'
		childFields = [
			Field( 'name',						self.tr('Name') ),
			Field( 'length',					self.tr('Length'),				format = ',', suffix = ' m' ),
			None,
			None,
		]
		
		super().__init__( fields, conduitRuns, childListName, childFields, parent )
	
	
	def newItem( self ) -> ConduitRun:
		'''
		Return a new `ConduitRun` to be used with `insertRows`.
		'''
		
		conduitRun = ConduitRun(
			name = self.tr('New Conduit Run'),
			length = 10.0,
		)
		
		return conduitRun