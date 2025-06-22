from functools import wraps
from typing import Any, Callable, ParamSpec, TypeVar

from ..core.current import get_tree

P = ParamSpec('P')
R = TypeVar('R')

__all__ = ['hook']

def hook(func: Callable[P, R]) -> Callable[P, R]:
    """
    Decorador base que convierte una función en un hook de Reactive.
    
    Proporciona el contexto necesario para que los hooks funcionen correctamente
    dentro de los componentes, gestionando el estado interno del hook.
    
    Args:
        func: Función a convertir en hook
        
    Returns:
        Función decorada que registra el hook en el componente actual
        
    Ejemplo:
        @hook
        def custom_hook():
            ...
    """
    @wraps(func)
    def decorator(*args: P.args, **kwargs: P.kwargs) -> Any:
        tree = get_tree()
        component = tree.get_current_component()
        component.state.active_hook()
        return func(*args, **kwargs)

    return decorator
