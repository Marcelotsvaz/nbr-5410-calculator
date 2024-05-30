# 
# NBR 5410 Calculator
# 
# 
# Author: Marcelo Tellier Sartori Vaz <marcelotsvaz@gmail.com>



from enum import StrEnum, auto
from functools import cache
from math import pi
from typing import Self

from pydantic import BaseModel, Field
from pyjson5 import decode_buffer

from nbr_5410_calculator.generic_model_views.models import GenericItem
from nbr_5410_calculator.installation.circuit import BaseCircuitUnion
from nbr_5410_calculator.installation.util import UniqueSerializable



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



class ConduitRun( UniqueSerializable, GenericItem ):
	'''
	Represents a conduit run containing multiple circuits.
	'''
	
	name: str
	length: float
	circuits: list[BaseCircuitUnion] = Field( default_factory = list )
	
	
	@property
	def conduit( self ) -> Conduit:
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
	def filledSection( self ) -> float:
		'''
		Sum of external section of all wires in this conduit run, in mm².
		'''
		
		return sum( circuit.wire.externalSection * circuit.supply.wireCount for circuit in self.circuits )
	
	
	@property
	def fillFactor( self ) -> float:
		'''
		Fraction of conduit area occupied by wires.
		'''
		
		return self.filledSection / self.conduit.section