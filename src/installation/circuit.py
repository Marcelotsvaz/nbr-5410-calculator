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
	
	'''
	
	COPPER = auto()
	ALUMINIUM = auto()



class WireInsulation( Enum ):
	'''
	
	'''
	
	PVC = auto()
	EPR = auto()
	XLPE = auto()



class WireConfiguration( Enum ):
	'''
	
	'''
	
	TWO = auto()
	THREE = auto()
	TWO_JUXTAPOSED = auto()
	THREE_TREFOIL = auto()
	THREE_JUXTAPOSED = auto()
	HORIZONTAL = auto()
	VERTICAL = auto()



@dataclass
class WireType:
	'''
	
	'''
	
	material: WireMaterial
	insulation: WireInsulation
	
	
	def getWireCapacities( self, method: ReferenceMethod, configuration: WireConfiguration ):
		'''
		
		'''
		
		material = self.material.name.lower()
		insulation = self.insulation.name.lower()
		
		with open( f'data/wireTypes/{material}-{insulation}.json5' ) as file:
			jsonData = decode_io( file )
			
			return OrderedDict( zip(
				jsonData['wireSections'],
				jsonData['referenceMethods'][method.name][configuration.name.lower()+'Wires']
			) )



class TemperatureCorrectionFactor:
	'''
	
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
	
	'''
	
	@classmethod
	def forGrouping( cls, grouping ):
		'''
		Return the correction factor for a given grouping.
		'''
		
		with open( 'data/groupingCorrectionFactor.json5' ) as file:
			factors = decode_io( file )
		
		last = max( factors.keys() )
		if grouping > int( last ):
			return factors[last]
		
		return factors[str( grouping )]



class Wire:
	'''
	
	'''
	
	def __init__( self, area ) -> None:
		self.area = area
	
	
	def __str__( self ) -> str:
		return f'{self.area:.2f}mm² Wire'
	
	
	def __eq__( self, other: Self ) -> bool:
		return self.area == other.area



class Breaker:
	'''
	
	'''
	
	@classmethod
	def getBreaker( cls, current ):
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
				return Wire( area )
		
		raise Exception( 'TODO: No wire.' )
	
	
	@property
	def breaker( self ):
		'''
		Suitable breaker for this circuit.
		'''
		
		return Breaker.getBreaker( self.projectCurrent )