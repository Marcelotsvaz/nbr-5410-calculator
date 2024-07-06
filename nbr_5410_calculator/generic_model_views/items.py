'''
Items and fields for `GenericItemModel`.
'''

from __future__ import annotations

from collections import defaultdict
from collections.abc import Callable, Generator, Iterable
from dataclasses import KW_ONLY, dataclass
from inspect import classify_class_attrs
from typing import Annotated, Any, Self, cast, get_origin, get_type_hints, override

from pydantic import BaseModel, ValidatorFunctionWrapHandler, computed_field, model_validator



def getTypeAnnotations( typeHint: type[Any] ) -> tuple[Any, ...]:
	'''
	Extract metadata from a type annotated with `Annotated`.
	'''
	
	if get_origin( typeHint ) is Annotated:
		return typeHint.__metadata__
	
	return ()



@dataclass
class ItemField:
	'''
	Field definition for a `GenericItem` sub-class.
	
	Ex.: `voltage: Annotated[float, ItemField( 'Voltage' )]`
	'''
	
	label: str | None = None
	_ = KW_ONLY
	format: str | Callable[[Any], str] | None = None
	editable: bool | None = None



@dataclass
class ItemFieldInfo:
	'''
	Concrete field defined from a `ItemField` instance.
	TODO: Make generic.
	'''
	
	name: str
	label: str
	_ = KW_ONLY
	format: str | Callable[[Any], str] = '{0}'
	editable: bool = False
	
	
	@classmethod
	def fromItemFieldList( cls, name: str, fields: Iterable[ItemField] ) -> Self:
		'''
		Create an instance of `ItemFieldInfo` by merging a list of `ItemField` instances.
		'''
		
		fieldInfoArgs: dict[str, Any] = {
			'name': name,
		}
		
		fieldNames = [
			'label',
			'format',
			'editable',
		]
		
		for field in fields:
			for fieldName in fieldNames:
				if ( value := getattr( field, fieldName ) ) is not None:
					fieldInfoArgs[fieldName] = value
		
		if 'label' not in fieldInfoArgs:
			fieldInfoArgs['label'] = fieldInfoArgs['name']
		
		return cls( **fieldInfoArgs )
	
	
	def valueType( self, instance: Any ) -> type:
		'''
		Return type of field in `instance`.
		'''
		
		return cast( type[Any], type( self.valueForEdition( instance ) ) )
	
	
	def valueForDisplay( self, instance: Any ) -> str:
		'''
		Return the formatted value of this field from `instance`.
		'''
		
		value = getattr( instance, self.name )
		
		if callable( self.format ):
			return str( self.format( value ) )
		
		return self.format.format( value )
	
	
	def valueForEdition( self, instance: Any ) -> Any:
		'''
		Return the raw value of this field from `instance`.
		'''
		
		return getattr( instance, self.name )
	
	
	def setValue( self, instance: Any, value: Any ) -> None:
		'''
		Set value of field in `instance`.
		'''
		
		setattr( instance, self.name, self.valueType( instance )( value ) )



class GenericItem( BaseModel ):
	'''
	Base class for items in a `GenericItemModel`.
	
	Attributes and properties annotated with `ItemField` are available in the model.
	'''
	
	@model_validator( mode = 'wrap' )
	@classmethod
	def deserializeAsSubclass(
		cls,
		data: Any | dict[str, Any],
		handler: ValidatorFunctionWrapHandler,
	) -> Self:
		'''
		Always deserialize instances of subclasses of this class as their actual class.
		'''
		
		if not isinstance( data, dict ) or '__type__' not in data:
			return handler( data )
		
		qualifiedName = data.pop( '__type__' )
		
		if not isinstance( qualifiedName, str ):
			raise TypeError( '`__type__` is not a valid class name.' )
		
		def iterSubclasses( baseClass: type[Self] ) -> Generator[type[Self], None, None]:
			yield baseClass
			
			for subclass in baseClass.__subclasses__():
				yield from iterSubclasses( subclass )
		
		for subclass in iterSubclasses( cls ):
			if qualifiedName == subclass.getQualifiedName():
				return subclass.model_validate( data )
		
		raise TypeError( f'`{qualifiedName}` is not a valid subclass of `{cls.getQualifiedName()}`.' )
	
	
	@classmethod
	def getQualifiedName( cls ) -> str:
		'''
		Qualified name of this class.
		'''
		
		return f'{cls.__module__}.{cls.__qualname__}'
	
	
	@computed_field
	def __type__( self ) -> str:
		'''
		Serialize qualified name.
		'''
		
		return self.getQualifiedName()
	
	
	def isValidChildren( self, item: GenericItem ) -> bool:	# pylint: disable = unused-argument
		'''
		Return `True` if `item` can be inserted as a child of this item.
		'''
		
		return False
	
	
	@property
	def children( self ) -> list[GenericItem]:
		'''
		List of child `GenericItem` instances.
		'''
		
		return []
	
	
	@classmethod
	def __getItemFields__( cls ) -> dict[str, list[ItemField]]:
		'''
		Get all `ItemField` instances for each class attribute.
		'''
		
		itemFields: dict[str, list[ItemField]] = defaultdict( list )
		
		for parent in cls.__bases__:
			if issubclass( parent, GenericItem ):
				for fieldName, parentItemFields in parent.__getItemFields__().items():
					itemFields[fieldName].extend( parentItemFields )
		
		# Get type hints from attributes.
		typeHintForMembers = {
			name: ( typeHint, True )
			for name, typeHint
			in get_type_hints( cls, include_extras = True ).items()
		}
		
		# Get type hints from properties, methods and class methods.
		for name, kind, defClass, member in classify_class_attrs( cls ):
			if defClass is not cls or kind not in [ 'property', 'method', 'class method' ]:
				continue
			
			editable = False
			if isinstance( member, property ):
				if not member.fget:
					continue
				
				editable = member.fset is not None
				member = member.fget
			
			try:
				returnTypeHint = get_type_hints( member, include_extras = True )['return']
				typeHintForMembers[name] = ( returnTypeHint, editable )
			except KeyError:
				pass
			except NameError:
				# TODO: Warning
				print( f'Skipping {name}.' )
		
		# Parse annotations from type hints.
		for name, ( typeHint, editable ) in typeHintForMembers.items():
			if not ( typeAnnotations := getTypeAnnotations( typeHint ) ):
				continue
			
			# Accumulate field properties.
			if not itemFields[name]:
				itemFields[name].append(
					ItemField(
						editable = editable,
					),
				)
			itemFields[name].extend(
				annotation for annotation in typeAnnotations
				if isinstance( annotation, ItemField )
			)
		
		return itemFields



class RootItem( GenericItem ):
	'''
	Root item for a `GenericItemModel`.
	'''
	
	childrenType: type[GenericItem]
	items: list[GenericItem]
	
	
	@override
	def isValidChildren( self, item: GenericItem ) -> bool:
		return isinstance( item, self.childrenType )
	
	
	@property
	@override
	def children( self ) -> list[GenericItem]:
		return self.items