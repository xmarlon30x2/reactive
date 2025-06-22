from typing import TYPE_CHECKING

from .use_effect import use_effect
from .hook import hook
from ..core.current import get_tree

if TYPE_CHECKING:
    from ..context import Context

__all__ = ['use_context']


@hook
def use_context[S](context: 'Context[S]') -> S:
    """
    Obtiene el valor actual de un contexto Reactivo.
    
    Suscribe el componente a las actualizaciones del contexto. Cuando el contexto cambie,
    el componente se volverá a renderizar automáticamente.
    
    Args:
        context: Contexto del cual obtener el valor
        
    Returns:
        Valor actual del contexto
    
    Ejemplo:
        theme = use_context(ThemeContext)
    """
    tree = get_tree()
    component = tree.get_current_component()
    value, id = context.get_current()
    
    @use_effect('')
    def _():
        context.clip(id=id, component=component)
        return lambda: context.unclip(id=id, component=component)
    
    return value
