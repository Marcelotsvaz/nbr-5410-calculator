# 
# NBR 5410 Calculator
# 
# 
# Author: Marcelo Tellier Sartori Vaz <marcelotsvaz@gmail.com>



from enum import Enum, auto
from dataclasses import dataclass
from collections import OrderedDict
from typing_extensions import Self	# TODO: Remove on Python 3.11.

from pyjson5 import decode_io



class ReferenceMethod( Enum ):
	'''
	Reference wire installation methods used to determine wire current capacity.
	
	See NBR 5410 6.2.5.1.2.
	'''
	
	A1 = auto()
	A2 = auto()
	B1 = auto()
	B2 = auto()
	C = auto()
	D = auto()
	E = auto()
	F = auto()
	G = auto()



class WireMaterial( Enum ):
	'''
	Wire conductor material.
	
	See NBR 5410 6.2.3.7.
	'''
	
	COPPER = 'copper'
	ALUMINIUM = 'aluminium'



class WireInsulation( Enum ):
	'''
	Wire insulation material.
	
	See NBR 5410 6.2.3.2.
	'''
	
	PVC = 'pvc'
	EPR = 'epr'
	XLPE = 'xlpe'



class WireConfiguration( Enum ):
	'''
	Number and layout of loaded wires for a specific reference method.
	
	See NBR 5410 tables 36~39.
	'''
	
	TWO = 'two'
	THREE = 'three'
	THREE_JUXTAPOSED = 'threeJuxtaposed'
	THREE_HORIZONTAL = 'threeHorizontal'
	THREE_VERTICAL = 'threeVertical'



@dataclass
class WireType:
	'''
	Represent all available sizes of an actual wire type used in a circuit.
	'''
	
	material: WireMaterial
	insulation: WireInsulation
	
	
	def __str__(self) -> str:
		return f'{self.insulation.name} {self.material.name} wire'
	
	
	def getWireCapacities( self, method: ReferenceMethod, configuration: WireConfiguration ):
		'''
		Get the current capacity for all sizes of this wire type for a given reference method and
		wire configuration.
		
		See NBR 5410 tables 36~39.
		'''
		
		with open( f'data/wireTypes/{self.material.value}-{self.insulation.value}.json5' ) as file:
			jsonData = decode_io( file )
			
			return OrderedDict( zip(
				jsonData['wireSections'],
				jsonData['referenceMethods'][method.name][configuration.value]
			) )



class TemperatureCorrectionFactor:
	'''
	Temperature correction factors for wire current capacity.
	
	See NBR 5410 6.2.5.3.
	'''
	
	@classmethod
	def forTemperature( cls, temperature ) -> float:
		'''
		Return the interpolated correction factor for a given temperature.
		'''
		
		with open( 'data/temperatureCorrectionFactor.json5' ) as file:
			factors = decode_io( file )
		
		if temperature <= factors[0]['temperature']:
			return factors[0]['value']
		
		for factor, nextFactor in zip( factors, factors[1:] ):
			if nextFactor['temperature'] >= temperature:
				return (
					factor['value'] +
					( nextFactor['value'] - factor['value'] ) *
					( temperature - factor['temperature'] ) / 
					( nextFactor['temperature'] - factor['temperature'] )
				)
		
		raise Exception( 'TODO: Temperature outside range.' )



class GroupingCorrectionFactor:
	'''
	Grouping correction factors for wire current capacity.
	
	See NBR 5410 6.2.5.5.
	'''
	
	@classmethod
	def forGrouping( cls, grouping ):
		'''
		Return the correction factor for a given circuit grouping.
		'''
		
		with open( 'data/groupingCorrectionFactor.json5' ) as file:
			factors = decode_io( file )
		
		last = max( factors.keys() )
		if grouping > int( last ):
			return factors[last]
		
		return factors[str( grouping )]



@dataclass
class Wire:
	'''
	WireType of a specific size.
	'''
	
	type: WireType
	area: float
	
	
	def __str__( self ) -> str:
		return f'{self.type}, {self.area:.2f}mm²'



class Breaker:
	'''
	Circuit breaker of a specific capacity.
	'''
	
	@classmethod
	def getBreaker( cls, current ):
		'''
		Return a suitable circuit breaker for a given current.
		'''
		
		return Breaker( current )
	
	
	def __init__( self, current ) -> None:
		self.current = current
	
	
	def __str__( self ) -> str:
		return f'{self.current:.1f}A Breaker'
	
	
	def __eq__( self, other: Self ) -> bool:
		return self.current == other.current



@dataclass
class Circuit:
	'''
	Represents a single circuit in an electrical installation.
	'''
	
	name: str
	
	power: float
	voltage: int
	phases: int
	grouping: int
	temperature: int
	referenceMethod: ReferenceMethod
	wireConfiguration: WireConfiguration
	wireType: WireType
	length: float
	
	description: str = None
	
	
	@property
	def current( self ):
		'''
		Apparent current.
		'''
		
		return self.power / self.voltage
	
	
	@property
	def projectCurrent( self ):
		'''
		Apparent current corrected for temperature and grouping.
		'''
		
		temperatureFactor = TemperatureCorrectionFactor.forTemperature( self.temperature )
		groupingFactor = GroupingCorrectionFactor.forGrouping( self.grouping )
		
		return self.current / temperatureFactor / groupingFactor
	
	
	@property
	def wire( self ):
		'''
		Suitable wire for this circuit considering current capacity, voltage drop and short-circuit
		current.
		'''
		
		capacities = self.wireType.getWireCapacities( self.referenceMethod, self.wireConfiguration )
		
		for area, current in capacities.items():
			if current >= self.projectCurrent:
				return Wire( self.wireType, area )
		
		raise Exception( 'TODO: No wire.' )
	
	
	@property
	def breaker( self ):
		'''
		Suitable breaker for this circuit.
		'''
		
		return Breaker.getBreaker( self.projectCurrent )