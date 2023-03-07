# 
# NBR 5410 Calculator
# 
# 
# Author: Marcelo Tellier Sartori Vaz <marcelotsvaz@gmail.com>



from PySide6.QtCore import QObject

from genericTableView import Field, GenericTableModel
from installation.circuit import (
	LoadType,
	WireMaterial,
	WireInsulation,
	WireType,
	ReferenceMethod,
	WireConfiguration,
	Circuit,
)



class CircuitsModel( GenericTableModel ):
	'''
	Map a list of `Circuit`s to a QTableView.
	'''
	
	def __init__( self, circuits: list[Circuit], parent: QObject | None = None ) -> None:
		'''
		Setup fields and load initial data.
		'''
		
		fields = [
			Field( 'name',						self.tr('Name') ),
			Field( 'power',						self.tr('Power'),			format = ',', suffix = ' VA' ),
			Field( 'loadType.value',			self.tr('Load Type'),		setter = 'loadType' ),
			Field( 'voltage',					self.tr('Voltage'),			format = ',', suffix = ' V' ),
			Field( 'phases',					self.tr('Phases') ),
			Field( 'grouping',					self.tr('Grouping') ),
			Field( 'temperature',				self.tr('Temperature'),		suffix = '°C' ),
			Field( 'referenceMethod.name',		self.tr('Ref. Method'),		setter = 'referenceMethod' ),
			Field( 'wireConfiguration.value',	self.tr('Configuration'),	setter = 'wireConfiguration' ),
			Field( 'wireType',					self.tr('Wire Type') ),
			Field( 'length',					self.tr('Length'),			format = ',', suffix = ' m' ),
			Field( 'current',					self.tr('Current'),			False, format = ',.1f', suffix = ' A' ),
			Field( 'breaker.current',			self.tr('Breaker'),			False, suffix = ' A' ),
			Field( 'wire.capacity',				self.tr('Wire Capacity'),	False, format = ',.1f', suffix = ' A' ),
			Field( 'wire.section',				self.tr('Wire Section'),	False, format = ',', suffix = ' mm²' ),
		]
		
		super().__init__( fields, circuits, parent )
	
	
	def newItem( self ) -> Circuit:
		'''
		Return a new `Circuit` to be used with `insertRows`.
		'''
		
		wireType = WireType( WireMaterial.COPPER, WireInsulation.PVC )
		circuit = Circuit(
			name				= self.tr('New Circuit'),
			loadType			= LoadType.POWER,
			voltage				= 127,
			phases				= 1,
			grouping			= 1,
			length				= 10.0,
			referenceMethod		= ReferenceMethod.B1,
			wireConfiguration	= WireConfiguration.TWO,
			wireType			= wireType,
			temperature			= 30,
			power				= 1000,
		)
		
		return circuit