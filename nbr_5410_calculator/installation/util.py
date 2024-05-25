# 
# NBR 5410 Calculator
# 
# 
# Author: Marcelo Tellier Sartori Vaz <marcelotsvaz@gmail.com>



from dataclasses import dataclass, field
from functools import partial
from typing import Any, ClassVar, Self, cast
from uuid import UUID, uuid4

from jsons import (
	default_object_deserializer,
	default_object_serializer,
	JsonSerializable,
	set_deserializer,
	set_serializer,
)



@dataclass( kw_only = True )
class UniqueSerializable( JsonSerializable ):
	'''
	Sub-class of `JsonSerializable` with defaults for dump and load methods.
	'''
	
	_dumpsKwargs = {
		'jdkwargs': {
			'indent': '\t',
			'sort_keys': True,
		}
	}
	
	
	# Class variables.
	_instances: ClassVar[dict[UUID, Self]] = {}
	
	
	# Instance variables.
	uuid: UUID = field( default_factory = uuid4 )
	
	
	def __post_init__( self ):
		self._instances[self.uuid] = self
	
	
	@classmethod
	def uniqueObjectDeserializer(
		cls,
		jsonDict: dict[str, Any],
		targetClass: type[Self],
		**kwargs: Any
	) -> Self:
		'''
		Deserialize an object, objects previously deserialized are returned from a cache instead.
		'''
		
		if 'uuid' in jsonDict:
			uuid = UUID( jsonDict['uuid'] )
			
			if uuid in cls._instances:
				return cls._instances[uuid]
		
		instance = cast( targetClass, default_object_deserializer( jsonDict, targetClass, **kwargs ) )
		cls._instances[instance.uuid] = instance
		
		return instance
	
	
	def dumps( self, **kwargs: Any ) -> str:
		kwargs = self._dumpsKwargs | kwargs
		
		return super().dumps( **kwargs )



set_deserializer(
	partial(
		UniqueSerializable.uniqueObjectDeserializer,
		strict = True,
	),
	UniqueSerializable,
)

set_serializer(
	partial(
		default_object_serializer,
		strip_privates = True,
		strip_properties = True,
	),
	UniqueSerializable,
)