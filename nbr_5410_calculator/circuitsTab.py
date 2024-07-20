'''
Models and view for the circuits tab.
'''

from typing import override

from PySide6.QtCore import QObject, Qt, Slot

from nbr_5410_calculator.generic_model_views.models import GenericItemModel, ModelIndex
from nbr_5410_calculator.generic_model_views.views import GenericTreeView
from nbr_5410_calculator.installation.circuit import (
	BaseCircuit,
	Circuit,
	UpstreamCircuit,
)
from nbr_5410_calculator.installation.project import Project



# 
# Models
#-------------------------------------------------------------------------------
class CircuitsModel( GenericItemModel[BaseCircuit] ):
	'''
	Recursive model of `BaseCircuit`.
	'''
	
	@override
	def __init__( self, project: Project, parent: QObject | None = None ) -> None:
		self.project = project
		
		super().__init__(
			datasource = self.project.circuits,
			dataTypes = [ BaseCircuit ],
			parent = parent,
		)
	
	
	@override
	def dragActionsForIndex( self, sourceIndex: ModelIndex ) -> Qt.DropAction:
		return Qt.DropAction.MoveAction



# 
# Views
#-------------------------------------------------------------------------------
class CircuitsView( GenericTreeView[CircuitsModel, BaseCircuit] ):
	'''
	Tree view of `BaseCircuit`.
	'''
	
	fieldOrder = {
		BaseCircuit: [
			'name',
			'supply',
			'loadType',
			'power',
			'wireType',
			'length',
			'current',
			'breaker',
			'_wireCapacity',
			'voltageDrop',
			'wire',
		],
	}
	
	
	@Slot()
	def newCircuit( self ) -> Circuit:
		'''
		Create new `Circuit`.
		'''
		
		project = self.model().project
		
		if not ( project.defaultLoadType and project.defaultSupply and project.defaultWireType ):
			raise Exception( 'TODO' )
		
		circuit = Circuit(
			length			= 10.0,
			loadPower		= 1000,
			loadType		= project.defaultLoadType,
			name			= self.tr('New Circuit'),
			project			= project,
			supply			= project.defaultSupply,
			wireType		= project.defaultWireType,
		)
		
		self.appendItem( circuit )
		
		return circuit
	
	
	@Slot()
	def newUpstreamCircuit( self ) -> UpstreamCircuit:
		'''
		Create new `UpstreamCircuit`.
		'''
		
		defaultLoadType = self.model().project.defaultLoadType
		defaultSupply = self.model().project.defaultSupply
		defaultWireType = self.model().project.defaultWireType
		
		if not ( defaultLoadType and defaultSupply and defaultWireType ):
			raise Exception( 'TODO' )
		
		circuit = UpstreamCircuit(
			length			= 10.0,
			loadType		= defaultLoadType,
			name			= self.tr('New Upstream Circuit'),
			supply			= defaultSupply,
			wireType		= defaultWireType,
		)
		
		self.appendItem( circuit )
		
		return circuit