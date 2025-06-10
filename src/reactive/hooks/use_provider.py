from typing import TYPE_CHECKING

from .use_ref import use_ref
from .use_id import use_id
from .hook import hook

if TYPE_CHECKING:
    from ..context import Context

__all__ = ['use_provider']

@hook
def use_provider[S](value: S, context: 'Context[S]'):
    last_value, set_last_value = use_ref(value)
    id = use_id()

    if last_value != set_last_value:
        set_last_value(value)
        context.update(id=id)

    return lambda: context.push(value=value, id=id)
