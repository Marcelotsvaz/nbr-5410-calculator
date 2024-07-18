'''
Top-level project model.
'''

from pydantic import Field, SerializeAsAny

from nbr_5410_calculator.installation.circuit import BaseCircuit, Supply, LoadType, WireType
from nbr_5410_calculator.installation.conduitRun import ConduitRun
from nbr_5410_calculator.installation.util import UniqueSerializable



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
	
	circuits: list[SerializeAsAny[BaseCircuit]] = Field( default_factory = list )
	conduitRuns: list[ConduitRun] = Field( default_factory = list )