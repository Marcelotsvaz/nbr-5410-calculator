# 
# NBR 5410 Calculator
# 
# 
# Author: Marcelo Tellier Sartori Vaz <marcelotsvaz@gmail.com>



from typing import Any, ClassVar, cast
from dataclasses import dataclass, field
from uuid import UUID, uuid4

from typing_extensions import Self
from jsons import JsonSerializable, set_deserializer, default_object_deserializer



@dataclass( kw_only = True )
class UniqueSerializable( JsonSerializable ):
	'''
	Sub-class of `JsonSerializable` with defaults for dump and load methods.
	'''
	
	_loadKwargs = {
		'strict': True,
	}
	
	_dumpKwargs = {
		'strip_properties': True,
		'strip_privates': True,
	}
	
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
	
	
	@classmethod
	def load( cls: type[Self], json_obj: object, **kwargs: Any ) -> Self:
		kwargs = cls._loadKwargs | kwargs
		
		return super().load( json_obj, **kwargs )
	
	
	@classmethod
	def loads( cls: type[Self], json_obj: str, **kwargs: Any ) -> Self:
		kwargs = cls._loadKwargs | kwargs
		
		return super().loads( json_obj, **kwargs )
	
	
	def dump( self, **kwargs: Any ) -> object:
		kwargs = self._dumpKwargs | kwargs
		
		return super().dump( **kwargs )
	
	
	def dumps( self, **kwargs: Any ) -> str:
		kwargs = self._dumpKwargs | self._dumpsKwargs | kwargs
		
		return super().dumps( **kwargs )



set_deserializer(
	UniqueSerializable.uniqueObjectDeserializer,
	UniqueSerializable,
	fork_inst = UniqueSerializable,
)