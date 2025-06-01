from typing import TYPE_CHECKING, Callable, Optional

from ..hooks.use_state import use_state
from ..components.component import component

if TYPE_CHECKING:
    from prompt_toolkit.layout.containers import AnyContainer

initial_value: Optional[Exception] = None

@component
def ErrorBoundary(fallback: Callable[[str, Exception], 'AnyContainer'], 
                 children: Callable[[], 'AnyContainer']) -> 'AnyContainer':
    """
    Componente para capturar errores en componentes hijos
    
    Args:
        fallback: Función que recibe la excepción y retorna componente alternativo
        children: Funcion de que crea el componente hijo a proteger
    """
    exception, set_exception = use_state(initial_value=initial_value)

    if not exception:
        try:
            return children()

        except Exception as exc:
            set_exception(exc)
            exception = exc
    
    return fallback('fallback', exception)
