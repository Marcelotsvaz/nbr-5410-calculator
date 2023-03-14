# 
# NBR 5410 Calculator
# 
# 
# Author: Marcelo Tellier Sartori Vaz <marcelotsvaz@gmail.com>



from typing import Any
from dataclasses import dataclass, field
from uuid import UUID, uuid4

from typing_extensions import Self

from jsons import JsonSerializable



@dataclass( kw_only = True )
class CustomJsonSerializable( JsonSerializable ):
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
	
	
	# Instance variables.
	id: UUID = field( default_factory = uuid4 )
	
	
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