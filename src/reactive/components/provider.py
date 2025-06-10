from reactive.components.component import component
from typing import TYPE_CHECKING, Any, Callable

from ..hooks.use_provider import use_provider

if TYPE_CHECKING:
    from prompt_toolkit.layout.containers import AnyContainer
    from ..context import Context

__all__ = ['Provider']

@component
def Provider(value: Any, context: 'Context[Any]', children: Callable[[], 'AnyContainer']):
    ctx = use_provider(value=value, context=context)
    with ctx():
        return children()
