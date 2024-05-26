# 
# NBR 5410 Calculator
# 
# 
# Author: Marcelo Tellier Sartori Vaz <marcelotsvaz@gmail.com>



from pydantic import Field

from .circuit import Supply, LoadType, WireType, BaseCircuit
from .conduitRun import ConduitRun
from .util import UniqueSerializable



class Project( UniqueSerializable ):
	'''
	Electrical installation project.
	'''
	
	name: str
	supplies: list[Supply] = Field( default_factory = list )
	loadTypes: list[LoadType] = Field( default_factory = list )
	wireTypes: list[WireType] = Field( default_factory = list )
	circuits: list[BaseCircuit] = Field( default_factory = list )
	conduitRuns: list[ConduitRun] = Field( default_factory = list )