# 
# NBR 5410 Calculator
# 
# 
# Author: Marcelo Tellier Sartori Vaz <marcelotsvaz@gmail.com>



from dataclasses import dataclass

from .circuit import Circuit
from .conduitRun import ConduitRun



@dataclass
class Project:
	'''
	Electrical installation project.
	'''
	
	name: str
	circuits: list[Circuit]
	conduitRuns: list[ConduitRun]