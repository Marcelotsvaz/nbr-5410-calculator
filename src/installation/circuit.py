# 
# NBR 5410 Calculator
# 
# 
# Author: Marcelo Tellier Sartori Vaz <marcelotsvaz@gmail.com>



from enum import Enum, auto
from dataclasses import dataclass
from typing_extensions import Self	# TODO: Remove on Python 3.11.

from pyjson5 import decode_io



class LoadType( Enum ):
	'''
	Load type to determine minimum wire section.
	
	See NBR 5410 6.2.6.1.1.
	'''
	
	LIGHTING = 'lighting'
	POWER = 'power'



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
	
	
	def __str__( self ) -> str:
		return f'{self.insulation.value}-insulated {self.material.value} wire'
	
	
	def getWires(
		self,
		referenceMethod: ReferenceMethod,
		wireConfiguration: WireConfiguration,
		correctionFactor: float,
	) -> list['Wire']:
		'''
		Get all wire sizes for a given reference method and wire configuration.
		
		See NBR 5410 tables 36~39.
		'''
		
		with open( f'data/wireTypes/{self.material.value}-{self.insulation.value}.json5' ) as file:
			jsonData = decode_io( file )
			sections = jsonData['wireSections']
			capacities = jsonData['referenceMethods'][referenceMethod.name][wireConfiguration.value]
		
		return [
			Wire( self, section, capacity, correctionFactor )
			for section, capacity in zip( sections, capacities )
		]



class TemperatureCorrectionFactor:
	'''
	Temperature correction factors for wire current capacity.
	
	See NBR 5410 6.2.5.3.
	'''
	
	@classmethod
	def forTemperature( cls, temperature: int ) -> float:
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
		
		raise ProjectError( 'TODO: Temperature outside range.' )



class GroupingCorrectionFactor:
	'''
	Grouping correction factors for wire current capacity.
	
	See NBR 5410 6.2.5.5.
	'''
	
	@classmethod
	def forGrouping( cls, grouping: int ) -> float:
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
	WireType of a specific size with capacity already calculated based on reference method,
	configuration, temperature and grouping.
	'''
	
	type: WireType
	section: float
	uncorrectedCapacity: float
	correctionFactor: float = 1.0
	
	
	def __str__( self ) -> str:
		return f'{self.type}, {self.section:.2f}mm²'
	
	
	def __gt__( self, other: Self ) -> bool:
		if self.type != other.type or self.correctionFactor != other.correctionFactor:
			return NotImplemented
		
		return self.capacity > other.capacity
	
	
	@property
	def capacity( self ) -> float:
		'''
		Current capacity corrected for temperature and grouping.
		'''
		
		return self.uncorrectedCapacity * self.correctionFactor



@dataclass
class Breaker:
	'''
	Circuit breaker of a specific capacity.
	'''
	
	current: int
	curve: str
	
	
	@classmethod
	def getBreakers( cls, curve: str ) -> list[Self]:
		'''
		Return breakers by curve.
		'''
		
		with open( 'data/breakers.json5' ) as file:
			breakers = decode_io( file )
		
		return [ Breaker( current, curve ) for current in breakers[curve] ]
	
	
	def __str__( self ) -> str:
		return f'{self.curve}{self.current} Breaker'
	
	
	def __gt__( self, other: Self ) -> bool:
		if self.curve != other.curve:
			return NotImplemented
		
		return self.current > other.current



@dataclass
class Circuit:
	'''
	Represents a single circuit in an electrical installation.
	'''
	
	name: str
	
	power: int
	loadType: LoadType
	voltage: int
	phases: int
	grouping: int
	temperature: int
	referenceMethod: ReferenceMethod
	wireConfiguration: WireConfiguration
	wireType: WireType
	length: float
	
	description: str | None = None
	
	
	@property
	def current( self ) -> float:
		'''
		Project current.
		'''
		
		return self.power / self.voltage
	
	
	@property
	def correctedCurrent( self ) -> float:
		'''
		Project current corrected for temperature and grouping.
		Used only for calculating wire section by current capacity.
		'''
		
		return self.current / self.correctionFactor
	
	
	@property
	def correctionFactor( self ) -> float:
		'''
		Correction factor for temperature and grouping.
		'''
		
		temperatureFactor = TemperatureCorrectionFactor.forTemperature( self.temperature )
		groupingFactor = GroupingCorrectionFactor.forGrouping( self.grouping )
		
		return temperatureFactor * groupingFactor
	
	
	@property
	def wire( self ) -> Wire:
		'''
		Suitable wire for this circuit considering current capacity, voltage drop and short-circuit
		current.
		'''
		
		return self.calculate()[0]
	
	
	@property
	def breaker( self ) -> Breaker:
		'''
		Suitable breaker for this circuit.
		'''
		
		return self.calculate()[1]
	
	
	def calculate( self ) -> tuple[Wire, Breaker]:
		'''
		Calculate wire and breaker for this circuit.
		'''
		
		wireByCriteria: dict[str, Wire] = {}
		allWires = self.wireType.getWires(
			self.referenceMethod,
			self.wireConfiguration,
			self.correctionFactor,
		)
		
		
		# Breaker
		breaker = min( filter(
			lambda breaker: breaker.current >= self.current,
			Breaker.getBreakers( 'C' ),
		) )
		if not breaker:
			raise ProjectError( 'No suitable breaker found.' )
		
		
		# Wire section by minimum section.
		if self.loadType == LoadType.LIGHTING:
			minimumSection = 1.5
		else:
			minimumSection = 2.5
		
		wireByCriteria['minimumSection'] = min( filter(
			lambda wire: wire.section >= minimumSection,
			allWires,
		) )
		
		
		# Wire section by current capacity.
		wireByCriteria['currentCapacity'] = min( filter(
			lambda wire: wire.capacity >= self.current,
			allWires,
		) )
		
		
		# Wire section by breaker.
		wireByCriteria['breaker'] = min( filter(
			lambda wire: wire.capacity >= breaker.current,
			allWires,
		) )
		
		
		# Select wire with largest section.
		wire = max( wireByCriteria.values() )
		if not wire:
			raise ProjectError( 'No suitable wire found.' )
		
		return wire, breaker



class ProjectError( Exception ):
	'''
	Base class for all project design errors.
	'''