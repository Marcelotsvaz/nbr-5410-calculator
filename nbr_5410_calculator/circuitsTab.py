'''
Models and view for the circuits tab.
'''

from typing import override

from PySide6.QtCore import QObject, Slot

from nbr_5410_calculator.generic_model_views.models import Field, GenericItemModel
from nbr_5410_calculator.generic_model_views.views import GenericTreeView
from nbr_5410_calculator.installation.circuit import (
	BaseCircuitUnion,
	ReferenceMethod,
	Circuit,
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
		
		fields = [
			Field( 'name',				self.tr('Name') ),
			Field( 'supply',			self.tr('Supply') ),
			Field( 'loadType.name',		self.tr('Load Type'),		setter = 'loadType' ),
			Field( 'power',				self.tr('Power'),			format = ',', suffix = ' VA' ),
			Field( 'referenceMethod',	self.tr('Ref. Method') ),
			Field( 'temperature',		self.tr('Temperature'),		suffix = '°C' ),
			Field( 'grouping',			self.tr('Grouping') ),
			Field( 'wireType',			self.tr('Wire Type') ),
			Field( 'length',			self.tr('Length'),			format = ',', suffix = ' m' ),
			Field( 'current',			self.tr('Current'),			False, format = ',.1f', suffix = ' A' ),
			Field( 'breaker.current',	self.tr('Breaker'),			False, suffix = ' A' ),
			Field( 'wire.capacity',		self.tr('Wire Capacity'),	False, format = ',.1f', suffix = ' A' ),
			Field( 'voltageDrop',		self.tr('Voltage Drop'),	False, format = '.1%' ),
			Field( 'wire.section',		self.tr('Wire Section'),	False, format = ',', suffix = ' mm²' ),
		]
		childListName = 'circuits'
		childFields = fields
		
		super().__init__( fields, self.project.circuits, childListName, childFields, parent )



# 
# Views
#-------------------------------------------------------------------------------
class CircuitsView( GenericTreeView[CircuitsModel, BaseCircuitUnion] ):
	'''
	`QTreeView` for `CircuitsModel`.
	'''
	
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