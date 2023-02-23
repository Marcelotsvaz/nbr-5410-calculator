# 
# NBR 5410 Calculator
# 
# 
# Author: Marcelo Tellier Sartori Vaz <marcelotsvaz@gmail.com>



import json

from dataclasses import dataclass
from typing_extensions import Self	# TODO: Remove on Python 3.11.



# class InstallMethod:
# 	'''
	
# 	'''



class ReferenceMethod:
	'''
	
	'''
	
	def __init__( self, code ) -> None:
		with open( f'data/referenceMethods/{code}.json' ) as file:
			self.currentCapacities = json.load( file )
	
	
	def GetWire( self, current ):
		for capacity in self.currentCapacities:
			if capacity['current'] > current:
				return Wire( capacity['area'] )
		
		raise Exception( 'TODO: No wire.' )



class TemperatureCorrectionFactor:
	'''
	
	'''
	
	@classmethod
	def forTemperature( cls, temperature ) -> float:
		'''
		Return the interpolated correction factor for a given temperature.
		'''
		
		with open( 'data/temperatureCorrectionFactor.json' ) as file:
			factors = json.load( file )
		
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
		
		with open( 'data/groupingCorrectionFactor.json' ) as file:
			factors = json.load( file )
		
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
	def GetBreaker( cls, current ):
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
		
		return self.referenceMethod.GetWire( self.projectCurrent )
	
	
	@property
	def breaker( self ):
		'''
		Suitable breaker for this circuit.
		'''
		
		return Breaker.GetBreaker( self.projectCurrent )