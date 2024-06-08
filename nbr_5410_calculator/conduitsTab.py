'''
Models and view for the conduits tab.
'''

from PySide6.QtCore import Slot

from nbr_5410_calculator.generic_model_views.models import GenericItemModel
from nbr_5410_calculator.generic_model_views.views import GenericListView, GenericTreeView
from nbr_5410_calculator.installation.circuit import BaseCircuit
from nbr_5410_calculator.installation.conduitRun import ConduitRun, ReferenceMethod



class ConduitRunsView(
	GenericTreeView[GenericItemModel[ConduitRun | BaseCircuit], ConduitRun | BaseCircuit],
):
	'''
	Tree view of `ConduitRun`.
	'''
	
	fieldOrder = {
		ConduitRun: [
			'name',
			'referenceMethod',
			'temperature',
			'length',
			'grouping',
			'fillFactor',
			'conduit',
		],
		BaseCircuit: [
			'name',
			None,
			None,
			'length',
			None,
			None,
			None,
		],
	}
	
	
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



class UnassignedCircuitsView( GenericListView[GenericItemModel[BaseCircuit], BaseCircuit] ):
	'''
	Flat list view of `BaseCircuit` that aren't assigned to any `ConduitRun`.
	'''
	
	fieldOrder = {
		BaseCircuit: [
			'name',
		]
	}