# 
# NBR 5410 Calculator
# 
# 
# Author: Marcelo Tellier Sartori Vaz <marcelotsvaz@gmail.com>



from dataclasses import dataclass, field

from .util import UniqueSerializable
from .circuit import BaseCircuit



@dataclass
class ConduitRun( UniqueSerializable ):
	'''
	Represents a conduit run containing multiple circuits.
	'''
	
	name: str
	length: float
	circuits: list[BaseCircuit] = field( default_factory = list )
	
	
	@property
	def diameter( self ):
		'''
		TODO
		'''
		
		return 25.4