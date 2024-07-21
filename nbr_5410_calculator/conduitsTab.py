'''
Models and view for the conduits tab.
'''

from collections.abc import Generator
from typing import override

from PySide6.QtCore import QModelIndex, QObject, Qt, Slot

from nbr_5410_calculator.circuitsTab import CircuitsModel
from nbr_5410_calculator.generic_model_views.items import GenericItem
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
	def rowCount( self, parent: ModelIndex = QModelIndex() ) -> int:
		if isinstance( self.itemFromIndex( parent ), BaseCircuit ):
			return 0
		
		return super().rowCount( parent )
	
	
	@override
	def dragActionsForIndex( self, sourceIndex: ModelIndex ) -> Qt.DropAction:
		return Qt.DropAction.MoveAction



class UnassignedCircuitsModel( GenericItemModel[BaseCircuit] ):
	'''
	Flat list of `BaseCircuit`.
	'''
	
	@override
	def __init__( self, circuitsModel: CircuitsModel, parent: QObject | None = None, ) -> None:
		super().__init__(
			datasource = [],
			dataTypes = [ BaseCircuit ],
			parent = parent,
		)
		
		self.circuitsModel = circuitsModel
		self.circuitsModel.rowsInserted.connect( self._refresh )
		self.circuitsModel.rowsRemoved.connect( self._refresh )
		self._refresh()
	
	
	@override
	def dragActionsForIndex( self, sourceIndex: ModelIndex ) -> Qt.DropAction:
		return Qt.DropAction.MoveAction
	
	
	@Slot()
	def _refresh( self ) -> None:
		'''
		Display all circuits not assigned to any conduit run.
		'''
		
		def iterCircuits( topCircuit: GenericItem ) -> Generator[BaseCircuit, None, None]:
			if isinstance( topCircuit, BaseCircuit ):
				yield topCircuit
			
			for circuit in topCircuit.children:
				yield from iterCircuits( circuit )
		
		self.layoutAboutToBeChanged.emit()
		self.root.items = [
			circuit
			for circuit in iterCircuits( self.circuitsModel.root )
			if not circuit.conduitRun
		]
		self.layoutChanged.emit()



# 
# Views
#-------------------------------------------------------------------------------
class ConduitRunsView( GenericTreeView[ConduitRunsModel, ConduitRun | BaseCircuit] ):
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