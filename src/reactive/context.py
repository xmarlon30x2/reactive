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
    """
    Gestor de contexto para compartir estado entre componentes.
    
    Atributos:
        _consumers: Registro de componentes suscritos al contexto
        _current: ContextVar que almacena el valor actual
        
    Métodos:
        push: Context manager para establecer un nuevo valor en el contexto
        update: Notifica a los componentes suscritos sobre cambios
        clip: Suscribe un componente a actualizaciones del contexto
        unclip: Elimina la suscripción de un componente
        get_current: Obtiene el valor actual del contexto
    """
    _consumers: Consumers
    _current: Current[S]

    def __init__(self, current: Current[S], consumers: Consumers):
        self._current = current
        self._consumers = consumers

    @contextmanager
    def push(self, value: S, id: str):
        """
        Context manager para establecer temporalmente un valor en el contexto.
        
        Args:
            value: Nuevo valor a establecer
            id: Identificador único para este valor
            
        Yields:
            None
            
        Garantiza:
            Restaura el valor anterior al salir del contexto
        """
        token = self._current.set((value, id))
        try:
            yield
        finally:
            self._current.reset(token)

    def update(self, id: str):
        """
        Notifica a todos los componentes suscritos que actualicen su estado.
        
        Args:
            id: Identificador del valor que cambió
        """
        for consumer in self._consumers[id]:
            consumer.set_dirty()

    def clip(self, id: str, component: 'Component') -> None:
        """
        Suscribe un componente a cambios en un contexto específico.
        
        Args:
            id: Identificador del valor a monitorear
            component: Componente a suscribir
        """
        self._consumers[id].add(component)
    
    def unclip(self, id: str, component: ' Component') -> None:
        """
        Elimina la suscripción de un componente a cambios en un contexto.
        
        Args:
            id: Identificador del valor
            component: Componente a desuscribir
        """
        self._consumers[id].discard(component)

    def get_current(self) -> tuple[S, str]:
        """
        Obtiene el valor actual del contexto y su identificador.
        
        Returns:
            Tupla (valor, id)
        """
        return self._current.get()

def create_context[S](default_value: S) -> 'Context[S]':
    """
    Factory para crear nuevos contextos reactivos.
    
    Args:
        default_value: Valor inicial del contexto
        
    Returns:
        Context[S]: Instancia de contexto configurada
        
    Nota:
        Cada contexto es independiente y gestiona sus propias suscripciones
    """
    current: Current[S] = ContextVar('value', default=(default_value, 'default'))
    consumers: Consumers = defaultdict(set)
    context = Context(current=current, consumers=consumers)
    return context
