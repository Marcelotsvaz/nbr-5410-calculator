# 
# NBR 5410 Calculator
# 
# 
# Author: Marcelo Tellier Sartori Vaz <marcelotsvaz@gmail.com>



from dataclasses import dataclass
from typing import Any
from typing_extensions import Self	# TODO: Remove on Python 3.11.

from .circuit import Circuit



@dataclass
class Project:
	'''
	Electrical installation project.
	'''
	
	name: str
	circuits: list[Circuit]
	
	
	@classmethod
	def fromJson( cls, json: dict[str, Any] ) -> Self:
		'''
		Deserialize from JSON.
		'''
		
		json['circuits'] = [ Circuit.fromJson( circuitJson ) for circuitJson in json['circuits'] ]
		
		return Project( **json )
	
	
	def toJson( self ) -> dict[str, Any]:
		'''
		Serialize into JSON.
		'''
		
		json = {
			'name': self.name,
			'circuits': [ circuit.toJson() for circuit in self.circuits ],
		}
		
		return json