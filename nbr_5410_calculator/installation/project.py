# 
# NBR 5410 Calculator
# 
# 
# Author: Marcelo Tellier Sartori Vaz <marcelotsvaz@gmail.com>



from pydantic import Field

from .circuit import BaseCircuitUnion, Supply, LoadType, WireType
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
	circuits: list[BaseCircuitUnion] = Field( default_factory = list )
	conduitRuns: list[ConduitRun] = Field( default_factory = list )