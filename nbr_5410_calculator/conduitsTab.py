'''
Models and view for the conduits tab.
'''

from PySide6.QtCore import Slot

from nbr_5410_calculator.generic_model_views.models import GenericItemModel
from nbr_5410_calculator.generic_model_views.views import GenericTreeView
from nbr_5410_calculator.installation.conduitRun import ConduitRun, ReferenceMethod



class ConduitRunsView( GenericTreeView[GenericItemModel[ConduitRun], ConduitRun] ):
	'''
	`QTreeView` for `ConduitRunsModel`.
	'''
	
	fieldOrder = [
		'name',
		'referenceMethod',
		'temperature',
		'length',
		'grouping',
		'fillFactor',
		'conduit',
	]
	
	
	@Slot()
	def newConduitRun( self ) -> ConduitRun:
		'''
		Create new `ConduitRun`.
		'''
		
		conduitRun = ConduitRun(
			name = self.tr('New Conduit Run'),
			referenceMethod	= ReferenceMethod.B1,
			temperature = 30,
			length = 10.0,
		)
		
		self.appendItem( conduitRun )
		
		return conduitRun