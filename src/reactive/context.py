from collections import defaultdict
from contextlib import contextmanager
from contextvars import ContextVar
from typing import Set, TYPE_CHECKING

if TYPE_CHECKING:
    from .core.component import Component

type Consumers = defaultdict[str, Set['Component']]
type Current[S] = ContextVar[tuple[S, str]]

__all__ = ['Context', 'create_context']

class Context[S]:
    _consumers: Consumers
    _current: Current[S]

    def __init__(self, current: Current[S], consumers: Consumers):
        self._current = current
        self._consumers = consumers

    @contextmanager
    def push(self, value: S, id: str):
        token = self._current.set((value, id))
        try:
            yield
        finally:
            self._current.reset(token)

    def update(self, id: str):
        for consumer in self._consumers[id]:
            consumer.set_dirty()

    def clip(self, id: str, component: 'Component') -> None:
        self._consumers[id].add(component)
    
    def unclip(self, id: str, component: ' Component') -> None:
        self._consumers[id].discard(component)

    def get_current(self) -> tuple[S, str]:
        return self._current.get()

def create_context[S](default_value: S) -> 'Context[S]':
    """
    Crea un nuevo contexto para compartir estado entre componentes
    
    Args:
        default_value: Valor por defecto del contexto
        
    Returns:
        Objeto contexto
    """
    current: Current[S] = ContextVar('value', default=(default_value, 'default'))
    consumers: Consumers = defaultdict(set)
    context = Context(current=current, consumers=consumers)
    return context
