from inspect import signature
from typing import Any, TYPE_CHECKING, Callable, Optional, TypeGuard, Union

if TYPE_CHECKING:
    from ..types import Setter, Computer

def is_compute(func: Callable[..., Any]) -> TypeGuard['Computer[Any]']:
    return len(signature(func).parameters) == 1

def is_setter(func: Callable[..., Any]) -> TypeGuard['Setter[Any]']:
    return len(signature(func).parameters) == 0

def factory_value[S](value: S, value_factory: Optional['Union[Setter[S], Computer[S]]'] = None) -> S:
    if not value_factory:
        return value
    if is_compute(value_factory):
        return value_factory(value)
    if is_setter(value_factory):
        return value_factory()
    return value
