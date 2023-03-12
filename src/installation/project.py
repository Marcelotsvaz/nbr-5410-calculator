# 
# NBR 5410 Calculator
# 
# 
# Author: Marcelo Tellier Sartori Vaz <marcelotsvaz@gmail.com>



from dataclasses import dataclass, field

from .circuit import BaseCircuit
from .conduitRun import ConduitRun
from .util import CustomJsonSerializable



@dataclass
class Project( CustomJsonSerializable ):
	'''
	Electrical installation project.
	'''
	
	name: str
	circuits: list[BaseCircuit] = field( default_factory = list )
	conduitRuns: list[ConduitRun] = field( default_factory = list )