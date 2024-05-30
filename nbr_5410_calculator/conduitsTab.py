'''
Models and view for the conduits tab.
'''

from typing import override

from PySide6.QtCore import QObject, Slot

from nbr_5410_calculator.generic_model_views.models import Field, GenericItemModel
from nbr_5410_calculator.generic_model_views.views import GenericTreeView
from nbr_5410_calculator.installation.conduitRun import ConduitRun



# 
# Models
#-------------------------------------------------------------------------------
class ConduitRunsModel( GenericItemModel[ConduitRun] ):
	'''
	Map a list of `ConduitRun`s to a `QTreeView`.
	'''
	
	@override
	def __init__( self, conduitRuns: list[ConduitRun], parent: QObject | None = None ) -> None:
		fields = [
			Field( 'name',						self.tr('Name') ),
			Field( 'length',					self.tr('Length'),				format = ',', suffix = ' m' ),
			Field( 'conduit.nominalDiameter',	self.tr('Diameter'),	False ),
			Field( 'fillFactor',				self.tr('Fill Factor'),	False,	format = '.1%' ),
		]
		childFields = [
			Field( 'name',						self.tr('Name') ),
			Field( 'length',					self.tr('Length'),				format = ',', suffix = ' m' ),
			None,
			None,
		]
		
		super().__init__( fields, conduitRuns, childFields, parent )



# 
# Views
#-------------------------------------------------------------------------------
class ConduitRunsView( GenericTreeView[ConduitRunsModel, ConduitRun] ):
	'''
	`QTreeView` for `ConduitRunsModel`.
	'''
	
	@Slot()
	def newConduitRun( self ) -> ConduitRun:
		'''
		Create new `ConduitRun`.
		'''
		
		conduitRun = ConduitRun(
			name = self.tr('New Conduit Run'),
			length = 10.0,
		)
		
		self.appendItem( conduitRun )
		
		return conduitRun