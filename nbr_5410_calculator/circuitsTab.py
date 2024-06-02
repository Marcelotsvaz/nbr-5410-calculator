'''
Models and view for the circuits tab.
'''

from typing import override

from PySide6.QtCore import QObject, Slot

from nbr_5410_calculator.generic_model_views.models import GenericItemModel
from nbr_5410_calculator.generic_model_views.views import GenericTreeView
from nbr_5410_calculator.installation.circuit import (
	BaseCircuit,
	BaseCircuitUnion,
	ReferenceMethod,
	Circuit,
	UpstreamCircuit,
)
from nbr_5410_calculator.installation.project import Project



# 
# Models
#-------------------------------------------------------------------------------
class CircuitsModel( GenericItemModel[BaseCircuitUnion] ):
	'''
	Map a list of `Circuit`s to a `QTreeView`.
	'''
	
	@override
	def __init__( self, project: Project, parent: QObject | None = None ) -> None:
		self.project = project
		
		super().__init__(
			datasource = self.project.circuits,
			dataType = BaseCircuit,
			parent = parent,
		)



# 
# Views
#-------------------------------------------------------------------------------
class CircuitsView( GenericTreeView[CircuitsModel, BaseCircuitUnion] ):
	'''
	`QTreeView` for `CircuitsModel`.
	'''
	
	fieldOrder = [
		'name',
		'supply',
		'loadType',
		'power',
		'referenceMethod',
		'temperature',
		'grouping',
		'wireType',
		'length',
		'current',
		'breaker',
		'wire',
		'_wireCapacity',
		'voltageDrop',
	]
	
	
	@Slot()
	def newCircuit( self ) -> Circuit:
		'''
		Create new `Circuit`.
		'''
		
		defaultLoadType = self.model().project.defaultLoadType
		defaultSupply = self.model().project.defaultSupply
		defaultWireType = self.model().project.defaultWireType
		
		if not ( defaultLoadType and defaultSupply and defaultWireType ):
			raise Exception( 'TODO' )
		
		circuit = Circuit(
			grouping		= 1,
			length			= 10.0,
			loadPower		= 1000,
			loadType		= defaultLoadType,
			name			= self.tr('New Circuit'),
			referenceMethod	= ReferenceMethod.B1,
			supply			= defaultSupply,
			temperature		= 30,
			wireType		= defaultWireType,
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
			grouping		= 1,
			length			= 10.0,
			loadType		= defaultLoadType,
			name			= self.tr('New Upstream Circuit'),
			referenceMethod	= ReferenceMethod.B1,
			supply			= defaultSupply,
			temperature		= 30,
			wireType		= defaultWireType,
		)
		
		self.appendItem( circuit )
		
		return circuit