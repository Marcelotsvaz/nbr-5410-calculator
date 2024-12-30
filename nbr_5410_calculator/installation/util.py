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
		# strict = True,	# TODO: Fix deserialization of StrEnum.
		extra = 'forbid',
	)
	__uuids__: ClassVar[dict[UUID, Self]] = {}
	
	# Fields.
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
		
		instance: Self = handler( data )
		
		if instance.uuid not in cls.__uuids__:
			cls.__uuids__[instance.uuid] = instance
		
		return cls.__uuids__[instance.uuid]
	
	
	@classmethod
	def clearInstanceRegistry( cls ) -> None:
		'''
		Remove all instances from the registry..
		'''
		
		cls.__uuids__.clear()



class ProjectError( Exception ):
	'''
	Base class for all project design errors.
	'''