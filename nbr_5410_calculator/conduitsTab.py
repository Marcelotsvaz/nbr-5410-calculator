'''
Models and view for the conduits tab.
'''

from typing import override
from PySide6.QtCore import Qt, Slot

from nbr_5410_calculator.circuitsTab import CircuitsModel
from nbr_5410_calculator.generic_model_views.models import GenericItemModel, ModelIndex
from nbr_5410_calculator.generic_model_views.views import GenericListView, GenericTreeView
from nbr_5410_calculator.installation.circuit import BaseCircuit
from nbr_5410_calculator.installation.conduitRun import ConduitRun, ReferenceMethod



# 
# Models
#-------------------------------------------------------------------------------
class ConduitRunsModel( GenericItemModel[ConduitRun | BaseCircuit] ):
	'''
	Two-level model of `ConduitRun` as parents of `BaseCircuit`.
	
	Allow external and internal drag-and-drop to assign circuits to conduit runs.
	'''
	
	@override
	def dragActionsForIndex( self, sourceIndex: ModelIndex ) -> Qt.DropAction:
		return Qt.DropAction.MoveAction



class UnassignedCircuitsModel( GenericItemModel[BaseCircuit] ):
	'''
	Flat list of `BaseCircuit`.
	'''
	
	@override
	def dragActionsForIndex( self, sourceIndex: ModelIndex ) -> Qt.DropAction:
		return Qt.DropAction.MoveAction
	
	
	@Slot()
	def addCircuit( self, parent: ModelIndex, first: int, last: int ) -> None:
		'''
		Insert circuit if it's not assigned to any conduit run.
		'''
		
		circuitModel = parent.model()
		
		if not isinstance( circuitModel, CircuitsModel ):
			raise TypeError( 'Signal from unsupported model.' )
		
		circuit = circuitModel.itemFromIndex( circuitModel.index( first, 0, parent ) )
		
		if not circuit.conduitRun:
			self.insertItem( circuit )
	
	
	@Slot()
	def removeCircuit( self, parent: ModelIndex, first: int, last: int ) -> None:
		'''
		Remove deleted circuit.
		'''
		
		circuitModel = parent.model()
		
		if not isinstance( circuitModel, CircuitsModel ):
			raise TypeError( 'Signal from unsupported model.' )
		
		removedCircuit = circuitModel.itemFromIndex( circuitModel.index( first, 0, parent ) )
		
		for index, circuit in enumerate( self.root.children ):
			if circuit is removedCircuit:
				self.removeRow( index, self.index( 0, 0 ) )
				break



# 
# Views
#-------------------------------------------------------------------------------
class ConduitRunsView(
	GenericTreeView[ConduitRunsModel, ConduitRun | BaseCircuit],
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