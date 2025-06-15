from reactive.components.component import component
from typing import TYPE_CHECKING, Callable, TypeVar

from ..hooks.use_provider import use_provider

if TYPE_CHECKING:
    from prompt_toolkit.layout.containers import AnyContainer
    from ..context import Context

__all__ = ['Provider']

V = TypeVar('V')

@component
def Provider(value: V, context: 'Context[V]', children: Callable[[], 'AnyContainer']):
    ctx = use_provider(value=value, context=context)
    with ctx():
        return children()
