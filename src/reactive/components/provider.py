from .component import component
from typing import TYPE_CHECKING, Callable, TypeVar

from ..hooks.use_provider import use_provider

if TYPE_CHECKING:
    from prompt_toolkit.layout.containers import AnyContainer
    from ..context import Context

__all__ = ['Provider']

V = TypeVar('V')

@component
def Provider(value: V, context: 'Context[V]', children: Callable[[], 'AnyContainer']):
    """
    Proveedor de contexto para componentes hijos.
    
    Args:
        value: Valor a proveer en el contexto
        context: Contexto Reactivo donde se proveerá el valor
        children: Función que renderiza los componentes hijos
        
    Returns:
        Contenedor con los hijos renderizados dentro del contexto
    """
    ctx = use_provider(value=value, context=context)
    with ctx():
        return children()
