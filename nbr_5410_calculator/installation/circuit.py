'''
`BaseCircuit` implementation, sub-classes and other models required by them.
'''

from __future__ import annotations

from enum import Enum, StrEnum, auto
from functools import cache
from math import pi
from typing import Annotated, Any, Self, override

from annotated_types import Ge, Gt, MinLen
from pydantic import BaseModel, Field, SerializeAsAny, SkipValidation
from pyjson5 import decode_buffer

from nbr_5410_calculator.generic_model_views.items import ItemField
from nbr_5410_calculator.generic_model_views.models import GenericItem
from nbr_5410_calculator.installation.util import ProjectError, UniqueSerializable



class Supply( UniqueSerializable, GenericItem ):
	'''
	Power supply feeding a `Circuit`. Eg.: 3 Phase 220V.
	'''
	
	voltage: Annotated[int, Ge( 0 ), ItemField( 'Voltage', format = '{0} V' )]
	phases: Annotated[int, Ge( 1 ), ItemField( 'Phases' )] = 1
	hasNeutral: Annotated[bool, ItemField( 'Neutral' )] = True
	hasGround: Annotated[bool, ItemField( 'Ground' )] = True
	
	
	@override
	def __str__( self ) -> str:
		neutral = '+N' if self.hasNeutral else ''
		
		return f'{self.voltage:,} V {self.phases}P{neutral}'
	
	
	@property
	def loadedWireCount( self ) -> int:
		'''
		Number of current carrying wires.
		'''
		
		return min( self.phases + self.hasNeutral, 3 )	# TODO: Support more than 3 loaded wires.
	
	
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
	
	name: Annotated[str, MinLen( 1 ), ItemField( 'Name' )]
	minimumWireSection: Annotated[float, Gt( 0.0 ), ItemField( 'Minimum Section' )]
	demandFactor: Annotated[float, Ge( 0.0 ), ItemField( 'Demand Factor' )]
	
	@override
	def __str__( self ) -> str:
		return self.name



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



class WireType( UniqueSerializable, GenericItem ):
	'''
	Represent all available sizes of an actual wire type used in a circuit.
	'''
	
	material: Annotated[WireMaterial, ItemField( 'Material' )]
	insulation: Annotated[WireInsulation, ItemField( 'Insulation' )]
	
	# TODO: Improve this.
	_resistivity: float
	_conductorSections: list[float]
	_conductorDiameters: list[float]
	_externalDiameters: list[float | None]
	_referenceMethods: dict[str, dict[str, list[float]]]
	
	
	@classmethod
	@cache
	def loadWires( cls, material: WireMaterial, insulation: WireInsulation ) -> dict[str, Any]:
		'''
		TODO: Proper class with Pydantic.
		'''
		
		with open( f'share/data/wireTypes/{material.value}-{insulation.value}.json5', 'rb' ) as file:
			return decode_buffer( file.read() )
	
	
	@override
	def model_post_init( self, __context: Any ) -> None:
		super().model_post_init( __context )
		
		wires = self.loadWires( self.material, self.insulation )
		
		self._resistivity = wires['resistivity']
		self._conductorSections = wires['conductorSections']
		self._conductorDiameters = wires['conductorDiameters']
		self._externalDiameters = wires['externalDiameters']
		self._referenceMethods = wires['referenceMethods']
	
	
	@override
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
	) -> list[Wire]:
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
	
	
	@override
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



class BreakerCurve( StrEnum ):
	'''
	Breaker curve.
	
	TODO: See NBR 5410 x.x.x.x.
	'''
	
	B = auto()
	C = auto()
	D = auto()



class Breaker( BaseModel ):
	'''
	Circuit breaker of a specific capacity.
	'''
	
	current: int
	curve: BreakerCurve
	
	
	@classmethod
	@cache
	def loadBreakers( cls ) -> dict[str, list[int]]:
		'''
		TODO: Proper class with Pydantic.
		'''
		
		with open( 'share/data/breakers.json5', 'rb' ) as file:
			return decode_buffer( file.read() )
	
	
	@classmethod
	def getBreakers( cls, curve: BreakerCurve ) -> list[Self]:
		'''
		Return breakers by curve.
		'''
		
		breakers = cls.loadBreakers()
		
		return [ cls( current = current, curve = curve ) for current in breakers[curve.value] ]
	
	
	@override
	def __str__( self ) -> str:
		return f'{self.curve}{self.current} Breaker'
	
	
	def __gt__( self, other: Self ) -> bool:
		if self.curve is not other.curve:
			return NotImplemented
		
		return self.current > other.current



class BaseCircuit( UniqueSerializable, GenericItem ):
	'''
	Abstract base class for a circuit in an electrical installation.
	'''
	
	name: Annotated[
		str,
		MinLen( 1 ),
		ItemField(
			'Name',
			description = 'Name identifying the circuit.',
		),
	]
	
	description: Annotated[
		str,
		ItemField(
			'Description',
			description = 'Description for this circuit.',
		),
	] = ''
	
	supply: Annotated[
		Supply,
		ItemField(
			'Supply',
			description = 'The supply for this circuit.',
			choices = lambda self: self.project.supplies
		),
	]
	
	loadType: Annotated[
		LoadType,
		ItemField(
			'Load Type',
			description = 'The type of load for this circuit.',
			choices = lambda self: self.project.loadTypes
		),
	]
	
	wireType: Annotated[
		WireType,
		ItemField(
			'Wire Type',
			description = 'Type of wire for this circuit.',
			choices = lambda self: self.project.wireTypes
		),
	]
	
	breakerCurve: Annotated[
		BreakerCurve,
		ItemField(
			'Breaker Curve',
			description = 'Breaker curve for this circuit.',
		),
	]
	
	length: Annotated[
		float,
		Ge( 0.0 ),
		ItemField(
			'Length',
			description = '',
			format = '{0:,} m',
		),
	]
	
	project: Annotated[SkipValidation[Project] | None, Field( exclude = True )] = None
	conduitRun: Annotated[ConduitRun | None, Field( exclude = True )] = None
	
	
	@property
	def power( self ) -> Annotated[
		float,
		ItemField(
			'Power',
			description = 'Apparent power consumed by this circuit.',
			format = '{0:,.0f} VA',
		),
	]:
		'''
		Apparent power consumed by this circuit.
		'''
		
		raise NotImplementedError()
	
	
	@power.setter
	def power( self, value: float ) -> None:
		raise NotImplementedError()
	
	
	@property
	def current( self ) -> Annotated[float, ItemField( 'Current', format = '{0:,.1f} A' )]:
		'''
		Project current.
		'''
		
		return self.power / self.supply.voltage / self.supply.phases
	
	
	@property
	def breaker( self ) -> Annotated[
		Breaker,
		ItemField( 'Breaker', format = lambda value: f'{value.current} A' )
	]:
		'''
		Suitable breaker for this circuit.
		'''
		
		breakers = list( filter(
			lambda breaker: breaker.current >= self.current,
			Breaker.getBreakers( self.breakerCurve ),
		) )
		
		if not breakers:
			raise ProjectError( 'No suitable breaker found.' )
		
		return min( breakers )
	
	
	@property
	def wire( self ) -> Annotated[
		Wire,
		ItemField( 'Wire Section', format = lambda value: f'{value.section:,.1f} mm²' )
	]:
		'''
		Suitable wire for this circuit considering current capacity, voltage drop and short-circuit
		current.
		'''
		
		wireByCriteria: dict[str, Wire] = {}
		if self.conduitRun:
			allWires = self.wireType.getWires(
				self.conduitRun.referenceMethod,
				self.supply.loadedWireCount,
				self.conduitRun.correctionFactor,
			)
		else:
			allWires = self.wireType.getWires(
				ReferenceMethod.A1,
				self.supply.loadedWireCount,
				1.0,
			)
		
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
			lambda wire: wire.capacity >= self.breaker.current,
			allWires,
		) )
		
		# Select wire with largest section.
		wire = max( wireByCriteria.values() )
		if not wire:
			raise ProjectError( 'No suitable wire found.' )
		
		return wire
	
	
	@property
	def _wireCapacity( self ) -> Annotated[float, ItemField( 'Wire Capacity', format = '{0:,.1f} A' )]:
		'''
		Wire capacity, as a direct field.
		'''
		
		return self.wire.capacity
	
	
	def _voltageDrop( self, wire: Wire ) -> float:
		'''
		Voltage drop as a fraction of nominal voltage.
		Helper function used to calculate voltage drop for different wire sizes.
		Used in `calculate()`.
		'''
		
		resistance = wire.resistancePerMeter * self.length * 2
		voltageDrop = self.current * resistance
		
		return voltageDrop / self.supply.voltage
	
	
	@property
	def voltageDrop( self ) -> Annotated[float, ItemField( 'Voltage Drop', format = '{0:.1%}' )]:
		'''
		Voltage drop as a fraction of nominal voltage.
		'''
		
		return self._voltageDrop( self.wire )



class Circuit( BaseCircuit ):
	'''
	Represents a single terminal circuit in an electrical installation.
	'''
	
	loadPower: Annotated[float, Ge( 0.0 )]	# TODO: Pydantic alias.
	
	
	@property
	@override
	def power( self ) -> float:
		return self.loadPower
	
	
	@power.setter
	@override
	def power( self, value: float ) -> None:
		self.loadPower = value



class UpstreamCircuit( BaseCircuit ):
	'''
	Represents a circuit whose load is a group of downstream circuits.
	'''
	
	circuits: list[SerializeAsAny[BaseCircuit]] = Field( default_factory = list )
	
	
	@property
	@override
	def power( self ) -> float:
		'''
		Total power consumed by all downstream circuits, corrected by each circuit's demand factor.
		'''
		
		return sum( circuit.power * circuit.loadType.demandFactor for circuit in self.circuits )
	
	
	@power.setter
	@override
	def power( self, value: float ) -> None:
		raise NotImplementedError()
	
	
	@property
	@override
	def children( self ) -> list[BaseCircuit]:
		return self.circuits
	
	
	@override
	def isChildValid( self, item: GenericItem ) -> bool:
		return isinstance( item, BaseCircuit )



# Import last due to circular dependencies.
# pylint: disable-next = wrong-import-position
from nbr_5410_calculator.installation.conduitRun import ConduitRun, ReferenceMethod
# pylint: disable-next = wrong-import-position
from nbr_5410_calculator.installation.project import Project