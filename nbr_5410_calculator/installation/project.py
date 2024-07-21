'''
Top-level project model.
'''

from typing import Generator, Iterable, Self
from pydantic import Field, SerializeAsAny, model_validator

from nbr_5410_calculator.installation.circuit import (
	BaseCircuit,
	LoadType,
	Supply,
	UpstreamCircuit,
	WireType,
)
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
	
	
	@model_validator( mode = 'after' )
	def _updateReferences( self ) -> Self:
		'''
		Update back-references in project's items.
		'''
		
		for circuit in self.iterCircuits():
			circuit.project = self
		
		for conduitRun in self.conduitRuns:
			for circuit in conduitRun.circuits:
				circuit.conduitRun = conduitRun
		
		return self
	
	
	def iterCircuits(
		self,
		circuits: Iterable[BaseCircuit] | None = None,
	) -> Generator[BaseCircuit, None, None]:
		'''
		Recursively iterate through all circuits in the project.
		'''
		
		if circuits is None:
			circuits = self.circuits
		
		for circuit in circuits:
			yield circuit
			
			if isinstance( circuit, UpstreamCircuit ):
				yield from self.iterCircuits( circuit.circuits )