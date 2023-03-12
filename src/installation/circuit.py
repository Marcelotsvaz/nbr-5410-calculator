# 
# NBR 5410 Calculator
# 
# 
# Author: Marcelo Tellier Sartori Vaz <marcelotsvaz@gmail.com>



from enum import Enum, auto
from dataclasses import dataclass
from typing_extensions import Self	# TODO: Remove on Python 3.11.

from pyjson5 import decode_io

from .util import CustomJsonSerializable



@dataclass
class Supply:
	'''
	Power supply feeding a `Circuit`. Eg.: 3 Phase 220V.
	'''
	
	voltage: int
	phases: int
	
	
	def __str__( self ) -> str:
		return f'{self.voltage:,} V {self.phases} Phase{"s" if self.phases > 1 else ""}'



@dataclass
class LoadType:
	'''
	Load type to determine minimum wire section and demand factor.
	
	See NBR 5410 6.2.6.1.1.
	'''
	
	name: str
	minimumWireSection: float
	demandFactor: float



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



class ReferenceMethod( Enum ):
	'''
	Reference wire installation methods used to determine wire current capacity.
	
	See NBR 5410 6.2.5.1.2.
	See NBR 5410 tables 36~39.
	'''
	
	A1 = auto()
	A2 = auto()
	B1 = auto()
	B2 = auto()
	C = auto()
	D = auto()
	E = auto()
	F = auto()
	F_JUXTAPOSED = auto()
	G_HORIZONTAL = auto()
	G_VERTICAL = auto()



@dataclass
class WireType:
	'''
	Represent all available sizes of an actual wire type used in a circuit.
	'''
	
	material: WireMaterial
	insulation: WireInsulation
	
	_resistivity: float
	_sections: list[float]
	_referenceMethods: dict[str, dict[str, list[float]]]
	
	
	def __init__( self, material: WireMaterial, insulation: WireInsulation ):
		with open( f'share/data/wireTypes/{material.value}-{insulation.value}.json5' ) as file:
			jsonData = decode_io( file )
		
		self.material = material
		self.insulation = insulation
		
		self._resistivity = jsonData['resistivity']
		self._sections = jsonData['wireSections']
		self._referenceMethods = jsonData['referenceMethods']
	
	
	def __str__( self ) -> str:
		return f'{self.insulation.value}-insulated {self.material.value} wire'
	
	
	@property
	def resistivity( self ):
		'''
		Resistivity in ohm meter.
		'''
		
		return self._resistivity
	
	
	def getWires(
		self,
		referenceMethod: ReferenceMethod,
		phases: int,
		correctionFactor: float,
	) -> list['Wire']:
		'''
		Get all wire sizes for a given reference method and wire configuration.
		
		See NBR 5410 tables 36~39.
		'''
		
		capacities = self._referenceMethods[referenceMethod.name][str( phases + 1 )]
		
		return [
			Wire( self, section, capacity, correctionFactor )
			for section, capacity in zip( self._sections, capacities )
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
		
		with open( 'share/data/temperatureCorrectionFactor.json5' ) as file:
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
		
		with open( 'share/data/groupingCorrectionFactor.json5' ) as file:
			factors = decode_io( file )
		
		last = max( factors.keys() )
		if grouping > int( last ):
			return factors[last]
		
		return factors[str( grouping )]



class VoltageDropLimit( float, Enum ):
	'''
	Voltage drop limits for different circuit sections.
	
	See NBR 5410 6.2.7.
	'''
	
	TERMINAL = 0.04



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
	
	
	@property
	def resistancePerMeter( self ) -> float:
		'''
		Wire resistance in ohm/meter.
		'''
		
		return self.type.resistivity / ( self.section / 1000**2 )



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
		
		with open( 'share/data/breakers.json5' ) as file:
			breakers = decode_io( file )
		
		return [ Breaker( current, curve ) for current in breakers[curve] ]
	
	
	def __str__( self ) -> str:
		return f'{self.curve}{self.current} Breaker'
	
	
	def __gt__( self, other: Self ) -> bool:
		if self.curve != other.curve:
			return NotImplemented
		
		return self.current > other.current



@dataclass( kw_only = True )
class BaseCircuit( CustomJsonSerializable ):
	'''
	Abstract base class for a circuit in an electrical installation.
	'''
	
	name: str
	
	loadType: LoadType
	supply: Supply
	grouping: int
	temperature: int
	referenceMethod: ReferenceMethod
	wireType: WireType
	length: float
	
	description: str | None = None
	
	
	@property
	def power( self ) -> float:
		'''
		Apparent power consumed by this circuit.
		'''
		
		raise NotImplementedError()
	
	
	@property
	def correctionFactor( self ) -> float:
		'''
		Correction factor for temperature and grouping.
		'''
		
		temperatureFactor = TemperatureCorrectionFactor.forTemperature( self.temperature )
		groupingFactor = GroupingCorrectionFactor.forGrouping( self.grouping )
		
		return temperatureFactor * groupingFactor
	
	
	@property
	def current( self ) -> float:
		'''
		Project current.
		'''
		
		return self.power / self.supply.voltage
	
	
	@property
	def correctedCurrent( self ) -> float:
		'''
		Project current corrected for temperature and grouping.
		Used only for calculating wire section by current capacity.
		'''
		
		return self.current / self.correctionFactor
	
	
	def _voltageDrop( self, wire: Wire ) -> float:
		'''
		Voltage drop as a fraction of nominal voltage.
		Helper function used to calculate voltage drop for different wire sizes.
		Used in `calculate()`.
		'''
		
		resistance = wire.resistancePerMeter * 2 * self.length
		voltageDrop = self.current * resistance
		
		return voltageDrop / self.supply.voltage
	
	
	@property
	def voltageDrop( self ) -> float:
		'''
		Voltage drop as a fraction of nominal voltage.
		'''
		
		return self._voltageDrop( self.wire )
	
	
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
			self.supply.phases,
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
		wireByCriteria['minimumSection'] = min( filter(
			lambda wire: wire.section >= self.loadType.minimumWireSection,
			allWires,
		) )
		
		
		# Wire section by current capacity.
		wireByCriteria['currentCapacity'] = min( filter(
			lambda wire: wire.capacity >= self.current,
			allWires,
		) )
		
		
		# Wire section by voltage drop.
		wireByCriteria['voltageDrop'] = min( filter(
			lambda wire: self._voltageDrop( wire ) <= VoltageDropLimit.TERMINAL,
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



@dataclass( kw_only = True )
class Circuit( BaseCircuit ):
	'''
	Represents a single terminal circuit in an electrical installation.
	'''
	
	loadPower: float
	
	
	@property
	def power( self ) -> float:
		return self.loadPower
	
	
	@power.setter
	def power( self, value: float ) -> None:
		self.loadPower = value



@dataclass( kw_only = True )
class UpstreamCircuit( BaseCircuit ):
	'''
	Represents a circuit whose load is a group of downstream circuits.
	'''
	
	circuits: list[BaseCircuit]
	
	
	@property
	def power( self ) -> float:
		'''
		Total power consumed by all downstream circuits, corrected by each circuit's demand factor.
		'''
		
		return sum( circuit.power * circuit.loadType.demandFactor for circuit in self.circuits )



class ProjectError( Exception ):
	'''
	Base class for all project design errors.
	'''