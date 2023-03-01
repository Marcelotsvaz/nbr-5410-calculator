#
# NBR 5410 Calculator
#
#
# Author: Marcelo Tellier Sartori Vaz <marcelotsvaz@gmail.com>



from typing import Any



def dump(
	obj: object,
	cls: type | None = ...,
	*,
	strict: bool = ...,
	fork_inst: type | None = ...,
	**kwargs: Any
) -> object:
	...


def dumps(
	obj: object,
	jdkwargs: dict[str, object] | None = ...,
	*args: Any,
	**kwargs: Any
) -> str:
	...


def dumpb(
	obj: object,
	encoding: str = ...,
	jdkwargs: dict[str, object] | None = ...,
	*args: Any,
	**kwargs: Any
) -> bytes:
	...