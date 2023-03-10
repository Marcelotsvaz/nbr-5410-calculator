# 
# NBR 5410 Calculator
# 
# 
# Author: Marcelo Tellier Sartori Vaz <marcelotsvaz@gmail.com>



from dataclasses import dataclass

from .util import CustomJsonSerializable



@dataclass
class ConduitRun( CustomJsonSerializable ):
	'''
	Represents a conduit run containing multiple circuits.
	'''
	
	name: str
	diameter: float
	length: float