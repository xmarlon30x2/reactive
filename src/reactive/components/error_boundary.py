from typing import Callable, TYPE_CHECKING, Optional

from ..hooks.use_id import use_id
from ..hooks.use_state import use_state
from ..components.component import component

if TYPE_CHECKING:
    from ..types import Node

__all__ = ['ErrorBoundary']

initial_value: Optional[Exception] = None

@component
def ErrorBoundary(
    fallback: Callable[[str, Exception], 'Node'],
    children: Callable[[], 'Node']
) -> 'Node':
    """
    Componente para capturar errores en componentes hijos
    
    Args:
        fallback: Función que recibe la excepción y retorna componente alternativo
        children: Funcion de que crea el componente hijo a proteger
    """
    # Estado para almacenar la excepción
    key = use_id()
    exception, set_exception = use_state(initial_value)
    
    # Si no hay error, intenta renderizar los hijos
    if exception is None: # type: ignore
        try:
            return children()
        except Exception as e:
            # Captura la excepción y actualiza el estado
            set_exception(e)
            # Renderiza el fallback inmediatamente
            return fallback(key, e)
    
    # Si hay un error almacenado, muestra el fallback
    return fallback(key, exception)
