from functools import wraps
from typing import TYPE_CHECKING, Callable, Optional, ParamSpec

from ..core.current import get_tree

if TYPE_CHECKING:
    from ..types import Node
    from prompt_toolkit.layout.containers import AnyContainer

P = ParamSpec('P')

__all__ = ['component']

def component(func: Callable[P, 'Node']):
    """
    Decorador que convierte funciones en componentes reactivos.
    
    Args:
        func: Función que retorna un nodo y puede usar hooks
        
    Returns:
        Función componente con capacidad de manejar estado y efectos
    """

    @wraps(func)
    def wraper(
            id: Optional[str] = None,
            key: Optional[str] = None,
            *args: P.args,
            **kwargs: P.kwargs,
        ) -> 'AnyContainer':
        tree = get_tree()
        kwargs['id'] = id
        kwargs['key'] = key
        component = tree.active_component(func, args, kwargs)
        return component.render_component(tree=tree, args=args, kwargs=kwargs)

    return wraper
