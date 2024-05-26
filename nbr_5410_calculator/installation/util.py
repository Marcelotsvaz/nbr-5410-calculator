# 
# NBR 5410 Calculator
# 
# 
# Author: Marcelo Tellier Sartori Vaz <marcelotsvaz@gmail.com>



from typing import Any, Self, cast
from uuid import UUID, uuid4

from pydantic import BaseModel, ConfigDict, Field, ValidationInfo, model_validator



class UniqueSerializable( BaseModel ):
	'''
	Sub-class of `BaseModel` that reuses previously deserialized instances that share the same UUID.
	'''
	
	# Class variables.
	model_config = ConfigDict(
		# TODO:
		# 'sort_keys': True,
		# 'indent': '\t',
		# strict = True,
		# strip_privates = True,
		# strip_properties = True,
	)
	
	# Fields.
	uuid: UUID = Field( default_factory = uuid4 )
	
	
	@model_validator( mode = 'after' )
	def shareInstanceByUuid( self, info: ValidationInfo ) -> Self:
		'''
		Reuse previously deserialized instances with the same UUID.
		'''
		
		context = cast( dict[UUID, Self] | Any, info.context )
		
		# No context used.
		if not isinstance( context, dict ):
			return self
		
		# New UUID.
		if self.uuid not in context:
			context[self.uuid] = self
			return self
		
		# Invalid instance.
		if self != context[self.uuid]:
			raise ValueError( 'A different instance with this UUID was already registered.' )
		
		# Return existing instance.
		return context[self.uuid]