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
	
	
	def __init__(
		self,
		name:str,
		circuits: list[Circuit] | None = None,
		conduitRuns: list[ConduitRun] | None = None
	) -> None:
		self.name = name
		self.circuits = circuits if circuits is not None else []
		self.conduitRuns = conduitRuns if conduitRuns is not None else []