'''
Base Pydantic model for all `Project` models.
'''

from typing import Annotated, Any, ClassVar, Self
from uuid import UUID, uuid4

from pydantic import (
	BaseModel,
	ConfigDict,
	Field,
	model_validator,
	PlainSerializer,
	ValidatorFunctionWrapHandler,
)



class UniqueSerializable( BaseModel ):
	'''
	Sub-class of `BaseModel` that reuses previously deserialized instances that share the same UUID.
	'''
	
	# Class variables.
	model_config = ConfigDict(
		# TODO:
		# 'sort_keys': True,
		# 'indent': '\t',
		validate_assignment = True,
		strict = True,
		extra = 'forbid',
	)
	
	# Fields.
	__uuids__: ClassVar[dict[str, Self]] = {}
	uuid: Annotated[
		UUID,
		Field( default_factory = uuid4 ),
		PlainSerializer( lambda uuid: str( uuid ) ),	# pylint: disable = unnecessary-lambda
	]
	
	
	@model_validator( mode = 'wrap' )
	@classmethod
	def _shareInstanceByUuid(
		cls,
		data: Any | dict[str, Any],
		handler: ValidatorFunctionWrapHandler,
	) -> Self:
		'''
		Reuse previously deserialized instances with the same UUID.
		'''
		
		if isinstance( data, dict ) and 'uuid' in data and data['uuid'] in cls.__uuids__:
			return cls.__uuids__[data['uuid']]
		
		instance: Self = handler( data )
		
		cls.__uuids__[str( instance.uuid )] = instance
		
		return instance



class ProjectError( Exception ):
	'''
	Base class for all project design errors.
	'''