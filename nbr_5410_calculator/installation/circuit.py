# 
# NBR 5410 Calculator
# 
# 
# Author: Marcelo Tellier Sartori Vaz <marcelotsvaz@gmail.com>



from enum import Enum, StrEnum, auto
from functools import cache
from math import pi
from typing import Any, Self

from pydantic import BaseModel, Field
from pyjson5 import decode_buffer

from nbr_5410_calculator.generic_model_views.models import GenericItem
from nbr_5410_calculator.installation.util import UniqueSerializable



class Supply( UniqueSerializable, GenericItem ):
	'''
	Power supply feeding a `Circuit`. Eg.: 3 Phase 220V.
	'''
	
	voltage: int
	phases: int = 1
	hasNeutral: bool = True
	hasGround: bool = True
	
	
	def __str__( self ) -> str:
		neutral = '+N' if self.hasNeutral else ''
		
		return f'{self.voltage:,} V {self.phases}P{neutral}'
	
	
	@property
	def loadedWireCount( self ) -> int:
		'''
		Number of current carrying wires.
		'''
		
		return self.phases if not self.hasNeutral else self.phases + 1
	
	
	@property
	def wireCount( self ) -> int:
		'''
		Number of wires.
		'''
		
		return self.phases + self.hasNeutral + self.hasGround



class LoadType( UniqueSerializable, GenericItem ):
	'''
	Load type to determine minimum wire section and demand factor.
	
	See NBR 5410 6.2.6.1.1.
	'''
	
	name: str
	minimumWireSection: float
	demandFactor: float



class WireMaterial( StrEnum ):
	'''
	Wire conductor material.
	
	See NBR 5410 6.2.3.7.
	'''
	
	COPPER = auto()
	ALUMINIUM = auto()



class WireInsulation( StrEnum ):
	'''
	Wire insulation material.
	
	See NBR 5410 6.2.3.2.
	'''
	
	PVC = auto()
	EPR = auto()
	XLPE = auto()



class ReferenceMethod( StrEnum ):
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



class WireType( UniqueSerializable, GenericItem ):
	'''
	Represent all available sizes of an actual wire type used in a circuit.
	'''
	
	material: WireMaterial
	insulation: WireInsulation
	
	# TODO: Improve this.
	_resistivity: float
	_conductorSections: list[float]
	_conductorDiameters: list[float]
	_externalDiameters: list[float | None]
	_referenceMethods: dict[str, dict[str, list[float]]]
	
	
	@classmethod
	@cache
	def load_wires( cls, material: WireMaterial, insulation: WireInsulation ) -> dict[str, Any]:
		'''
		TODO: Proper class with Pydantic.
		'''
		
		with open( f'share/data/wireTypes/{material.value}-{insulation.value}.json5', 'rb' ) as file:
			return decode_buffer( file.read() )
	
	
	# TODO: Fix signature.
	def __init__( self, **kwargs: Any ) -> None:
		super().__init__( **kwargs )
		
		wires = self.load_wires( self.material, self.insulation )
		
		self._resistivity = wires['resistivity']
		self._conductorSections = wires['conductorSections']
		self._conductorDiameters = wires['conductorDiameters']
		self._externalDiameters = wires['externalDiameters']
		self._referenceMethods = wires['referenceMethods']
	
	
	def __str__( self ) -> str:
		return f'{self.insulation.value}-insulated {self.material.value} wire'
	
	
	@property
	def resistivity( self ) -> float:
		'''
		Resistivity in ohm meter.
		'''
		
		return self._resistivity
	
	
	def getWires(
		self,
		referenceMethod: ReferenceMethod,
		loadedWireCount: int,
		correctionFactor: float,
	) -> list['Wire']:
		'''
		Get all wire sizes for a given reference method and wire configuration.
		
		See NBR 5410 tables 36~39.
		'''
		
		capacities = self._referenceMethods[referenceMethod.name][str( loadedWireCount )]
		
		return [
			Wire(
				type = self,
				section = section,
				uncorrectedCapacity = uncorrectedCapacity,
				conductorDiameter = conductorDiameter,
				externalDiameter = externalDiameter,
				correctionFactor = correctionFactor,
			)
			for section, uncorrectedCapacity, conductorDiameter, externalDiameter in zip(
				self._conductorSections,
				capacities,
				self._conductorDiameters,
				self._externalDiameters,
			)
			# TODO: Remove this.
			if externalDiameter is not None
		]



class TemperatureCorrectionFactor:
	'''
	Temperature correction factors for wire current capacity.
	
	See NBR 5410 6.2.5.3.
	'''
	
	@classmethod
	@cache
	def load_factors( cls ) -> list[dict[str, Any]]:
		'''
		TODO: Proper class with Pydantic.
		'''
		
		with open( 'share/data/temperatureCorrectionFactor.json5', 'rb' ) as file:
			return decode_buffer( file.read() )
	
	
	@classmethod
	def forTemperature( cls, temperature: int ) -> float:
		'''
		Return the interpolated correction factor for a given temperature.
		'''
		
		factors = cls.load_factors()
		
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
	@cache
	def load_factors( cls ) -> dict[str, float]:
		'''
		TODO: Proper class with Pydantic.
		'''
		
		with open( 'share/data/groupingCorrectionFactor.json5', 'rb' ) as file:
			return decode_buffer( file.read() )
	
	
	@classmethod
	def forGrouping( cls, grouping: int ) -> float:
		'''
		Return the correction factor for a given circuit grouping.
		'''
		
		factors = cls.load_factors()
		
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



class Wire( BaseModel ):
	'''
	WireType of a specific size with capacity already calculated based on reference method,
	configuration, temperature and grouping.
	'''
	
	type: WireType
	section: float
	uncorrectedCapacity: float
	conductorDiameter: float
	externalDiameter: float
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
	
	
	@property
	def externalSection( self ) -> float:
		'''
		Wire external section in mm².
		'''
		
		return pi * ( self.externalDiameter / 2 ) ** 2



class Breaker( BaseModel ):
	'''
	Circuit breaker of a specific capacity.
	'''
	
	current: int
	curve: str
	
	
	@classmethod
	@cache
	def load_breakers( cls ) -> dict[str, list[int]]:
		'''
		TODO: Proper class with Pydantic.
		'''
		
		with open( 'share/data/breakers.json5', 'rb' ) as file:
			return decode_buffer( file.read() )
	
	
	@classmethod
	def getBreakers( cls, curve: str ) -> list[Self]:
		'''
		Return breakers by curve.
		'''
		
		breakers = cls.load_breakers()
		
		return [ cls( current = current, curve = curve ) for current in breakers[curve] ]
	
	
	def __str__( self ) -> str:
		return f'{self.curve}{self.current} Breaker'
	
	
	def __gt__( self, other: Self ) -> bool:
		if self.curve != other.curve:
			return NotImplemented
		
		return self.current > other.current



class BaseCircuit( UniqueSerializable, GenericItem ):
	'''
	Abstract base class for a circuit in an electrical installation.
	'''
	
	name: str
	description: str = ''
	
	loadType: LoadType
	supply: Supply
	grouping: int
	temperature: int
	referenceMethod: ReferenceMethod
	wireType: WireType
	length: float
	
	
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
			self.supply.loadedWireCount,
			self.correctionFactor,
		)
		
		
		# Breaker
		breaker = min( filter(
			lambda breaker: breaker.current >= self.current,
			Breaker.getBreakers( 'C' ),
		) )
		if not breaker:	# TODO: This check is wrong. filter raises.
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



class UpstreamCircuit( BaseCircuit ):
	'''
	Represents a circuit whose load is a group of downstream circuits.
	'''
	
	circuits: list['BaseCircuitUnion'] = Field( default_factory = list )
	
	
	@property
	def power( self ) -> float:
		'''
		Total power consumed by all downstream circuits, corrected by each circuit's demand factor.
		'''
		
		return sum( circuit.power * circuit.loadType.demandFactor for circuit in self.circuits )
	
	
	@property
	def children( self ) -> list[Self]:
		return self.circuits



# For Pydantic serialization of derived classes.
BaseCircuitUnion = Circuit | UpstreamCircuit



class ProjectError( Exception ):
	'''
	Base class for all project design errors.
	'''