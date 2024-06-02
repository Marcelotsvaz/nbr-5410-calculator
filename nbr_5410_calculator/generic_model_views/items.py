'''
Items and fields for `GenericItemModel`.
'''

from __future__ import annotations

from collections import defaultdict
from collections.abc import Callable, Iterable
from dataclasses import KW_ONLY, dataclass
from inspect import getmembers
from typing import Annotated, Any, ClassVar, Self, cast, get_origin, get_type_hints

from pydantic import BaseModel



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
	
	__itemFields__: ClassVar[dict[str, list[ItemField]]] = defaultdict( list )
	
	
	@property
	def children( self ) -> list[GenericItem] | None:
		'''
		List of child `GenericItem` instances, if this item supports children.
		'''
		
		return None
	
	
	@classmethod
	def __pydantic_init_subclass__( cls, **kwargs: Any ):
		super().__pydantic_init_subclass__( **kwargs )
		
		cls.__itemFields__ = cls.__itemFields__.copy()
		
		# Get fields from attributes.
		for name, typeHint in get_type_hints( cls, include_extras = True ).items():
			if not ( typeAnnotations := getTypeAnnotations( typeHint ) ):
				continue
			
			# Accumulate field properties.
			cls.__itemFields__[name].append(
				ItemField(
					editable = True,
				),
			)
			cls.__itemFields__[name].extend(
				annotation for annotation in typeAnnotations
				if isinstance( annotation, ItemField )
			)
		
		# Get fields from properties.
		for name, member in getmembers( cls ):
			if not isinstance( member, property ) or not member.fget:
				continue
				
			returnTypeHint = get_type_hints( member.fget, include_extras = True ).get( 'return' )
			
			if not returnTypeHint or not ( typeAnnotations := getTypeAnnotations( returnTypeHint ) ):
				continue
			
			# Accumulate field properties.
			cls.__itemFields__[name].append(
				ItemField(
					editable = member.fset is not None,
				),
			)
			cls.__itemFields__[name].extend(
				annotation for annotation in typeAnnotations
				if isinstance( annotation, ItemField )
			)



class RootItem( GenericItem ):
	'''
	Root item for a `GenericItemModel`.
	'''
	
	items: list[GenericItem]
	
	
	@property
	def children( self ) -> list[GenericItem]:
		return self.items