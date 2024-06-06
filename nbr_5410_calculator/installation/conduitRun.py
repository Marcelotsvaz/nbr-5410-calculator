'''
Models related to conduits.
'''

from __future__ import annotations

from enum import StrEnum, auto
from functools import cache
from math import pi
from typing import Annotated, Any, Self

from pydantic import BaseModel, Field
from pyjson5 import decode_buffer

from nbr_5410_calculator.generic_model_views.items import ItemField
from nbr_5410_calculator.generic_model_views.models import GenericItem
from nbr_5410_calculator.installation.circuit import BaseCircuitUnion
from nbr_5410_calculator.installation.util import ProjectError, UniqueSerializable



class ConduitType( StrEnum ):
	'''
	Type of conduit.
	'''
	
	RIGID = auto()
	FLEXIBLE = auto()



class Conduit( BaseModel ):
	'''
	Conduit of specific type and size.
	'''
	
	conduitType: ConduitType
	nominalDiameter: str
	externalDiameter: float
	internalDiameter: float
	# TODO: Validate diameters.
	
	brand: str = ''
	model: str = ''
	
	
	@classmethod
	@cache
	def allConduits( cls ) -> list[Self]:
		'''
		Return all available sizes of this model of conduit.
		'''
		
		# TODO: Proper class with Pydantic.
		with open( 'share/data/conduit/rigid.json5', 'rb' ) as file:
			jsonData = decode_buffer( file.read() )
		
		conduitType = ConduitType( jsonData['conduitType'] )
		nominalDiameters = jsonData['nominalDiameters']
		externalDiameters = jsonData['externalDiameters']
		internalDiameters = jsonData['internalDiameters']
		
		brand = jsonData['brand']
		model = jsonData['model']
		
		conduits = [
			cls(
				conduitType = conduitType,
				nominalDiameter = nominalDiameter,
				externalDiameter = externalDiameter,
				internalDiameter = internalDiameter,
				brand = brand,
				model = model,
			)
			for nominalDiameter, externalDiameter, internalDiameter
			in zip( nominalDiameters, externalDiameters, internalDiameters )
		]
		
		return conduits
	
	
	def __gt__( self, other: Self ) -> bool:
		return self.section > other.section
	
	
	@property
	def section( self ) -> float:
		'''
		Internal section in mm².
		'''
		
		return pi * ( self.internalDiameter / 2 ) ** 2



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



class TemperatureCorrectionFactor:
	'''
	Temperature correction factors for wire current capacity.
	
	See NBR 5410 6.2.5.3.
	'''
	
	@classmethod
	@cache
	def loadFactors( cls ) -> list[dict[str, Any]]:
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
		
		factors = cls.loadFactors()
		
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
	def loadFactors( cls ) -> dict[str, float]:
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
		
		factors = cls.loadFactors()
		
		last = max( factors.keys() )
		if grouping > int( last ):
			return factors[last]
		
		return factors[str( grouping )]



class ConduitRun( UniqueSerializable, GenericItem ):
	'''
	Represents a conduit run containing multiple circuits.
	'''
	
	name: Annotated[str, ItemField( 'Name' )]
	referenceMethod: Annotated[ReferenceMethod, ItemField( 'Ref. Method' )]
	temperature: Annotated[int, ItemField( 'Temperature', format = '{0}°C' )]
	length: Annotated[float, ItemField( 'Length', format = '{0:,} m' )]
	
	circuits: list[BaseCircuitUnion] = Field( default_factory = list )
	
	
	@property
	def conduit( self ) -> Annotated[
		Conduit,
		ItemField( 'Diameter', format = lambda value: value.nominalDiameter ),
	]:
		'''
		TODO
		'''
		
		match sum( circuit.supply.wireCount for circuit in self.circuits ):
			case 1:
				maxFillFactor = 0.53
			case 2:
				maxFillFactor = 0.31
			case _:
				maxFillFactor = 0.40
		
		conduit = min( filter(
			lambda conduit: conduit.section * maxFillFactor >= self.filledSection,
			Conduit.allConduits(),
		) )
		
		return conduit
	
	
	@property
	def grouping( self ) -> Annotated[int, ItemField( 'Grouping' )]:
		'''
		Number of circuits in run.
		'''
		
		return len( self.circuits )
	
	
	@property
	def correctionFactor( self ) -> float:
		'''
		Correction factor for temperature and grouping.
		'''
		
		temperatureFactor = TemperatureCorrectionFactor.forTemperature( self.temperature )
		groupingFactor = GroupingCorrectionFactor.forGrouping( self.grouping )
		
		return temperatureFactor * groupingFactor
	
	
	@property
	def filledSection( self ) -> float:
		'''
		Sum of external section of all wires in this conduit run, in mm².
		'''
		
		return sum( circuit.wire.externalSection * circuit.supply.wireCount for circuit in self.circuits )
	
	
	@property
	def fillFactor( self ) -> Annotated[float, ItemField( 'Fill Factor', format = '{0:.1%}' )]:
		'''
		Fraction of conduit area occupied by wires.
		'''
		
		return self.filledSection / self.conduit.section
	
	
	@property
	def children( self ) -> list[BaseCircuitUnion]:
		return self.circuits