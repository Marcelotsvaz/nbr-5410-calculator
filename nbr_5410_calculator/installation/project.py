'''
Project model.
'''

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
	
	defaultSupply: Supply | None = None
	defaultLoadType: LoadType | None = None
	defaultWireType: WireType | None = None
	
	circuits: list[BaseCircuitUnion] = Field( default_factory = list )
	conduitRuns: list[ConduitRun] = Field( default_factory = list )