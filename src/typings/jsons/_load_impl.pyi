# 
# NBR 5410 Calculator
# 
# 
# Author: Marcelo Tellier Sartori Vaz <marcelotsvaz@gmail.com>



from typing import Type, Callable, Any

from jsons._common_impl import T



def load(
	json_obj: object,
	cls: Type[T] | None = ...,
	*,
	strict: bool = ...,
	fork_inst: type | None = ...,
	attr_getters: dict[str, Callable[[], object]] | None = ...,
	**kwargs: Any
) -> T:
	...


def loads(
	str_: str,
	cls: Type[T] | None = ...,
	jdkwargs: dict[str, object] | None = ...,
	*args: Any,
	**kwargs: Any
) -> T:
	...


def loadb(
	bytes_: bytes,
	cls: Type[T] | None = ...,
	encoding: str = ...,
	jdkwargs: dict[str, object] | None = ...,
	*args: Any,
	**kwargs: Any
) -> T:
	...