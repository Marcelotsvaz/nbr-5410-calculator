'''
Base Pydantic model for all `Project` models.
'''

from typing import Annotated, Any, Self, cast
from uuid import UUID, uuid4

from pydantic import BaseModel, ConfigDict, Field, PlainSerializer, ValidationInfo, model_validator



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
		extra = 'forbid',
	)
	
	# Fields.
	uuid: Annotated[
		UUID,
		Field( default_factory = uuid4 ),
		PlainSerializer( lambda uuid: str( uuid ) ),	# pylint: disable = unnecessary-lambda
	]
	
	
	# TODO: Wrap so we don't construct the class unnecessarily.
	@model_validator( mode = 'after' )
	def shareInstanceByUuid( self, info: ValidationInfo ) -> Self:
		'''
		Reuse previously deserialized instances with the same UUID.
		'''
		
		context = cast( dict[str, Self] | Any, info.context )
		
		# No context used.
		if not isinstance( context, dict ):
			return self
		
		# New UUID.
		if self.uuid.hex not in context:
			context[self.uuid.hex] = self
			return self
		
		# Invalid instance.
		if self != context[self.uuid.hex]:
			raise ValueError( 'A different instance with this UUID was already registered.' )
		
		# Return existing instance.
		return context[self.uuid.hex]



class ProjectError( Exception ):
	'''
	Base class for all project design errors.
	'''