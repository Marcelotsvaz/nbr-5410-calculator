# 
# NBR 5410 Calculator
# 
# 
# Author: Marcelo Tellier Sartori Vaz <marcelotsvaz@gmail.com>



import json



class Circuit:
	'''
	Represents a single circuit in an electrical installation.
	'''
	
	def __init__( self, **kwargs ) -> None:
		# Identity.
		self.name = kwargs['name']
		self.description = kwargs.get( 'description' )
		
		# Installation.
		self.voltage = kwargs['voltage']
		self.phases = kwargs['phases']
		self.grouping = kwargs['grouping']
		self.length = kwargs['length']
		self.referenceMethod = kwargs['referenceMethod']
		self.temperature = kwargs['temperature']
		
		# Load.
		self.power = kwargs['power']
	
	
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
		
		'''
		
		return self.referenceMethod.GetWire( self.projectCurrent )
	
	
	@property
	def breaker( self ):
		'''
		
		'''
		
		return Breaker.GetBreaker( self.projectCurrent )



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
				return Wire( capacity['area'], capacity['current'] )
		
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
	
	def __init__( self, area, current ) -> None:
		self.area = area
		self.current = current
	
	
	def __str__( self ) -> str:
		return f'{self.area:.2f}mm² Wire'



class Breaker:
	'''
	
	'''
	
	@classmethod
	def GetBreaker( cls, current ):
		return Breaker( current )
	
	
	def __init__( self, current ) -> None:
		self.current = current
	
	
	def __str__( self) -> str:
		return f'{self.current:.1f}A Breaker'