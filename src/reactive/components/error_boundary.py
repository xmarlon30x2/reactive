from typing import TYPE_CHECKING, Callable, Optional

from ..hooks.use_state import use_state
from ..components.component import component

if TYPE_CHECKING:
    from prompt_toolkit.layout.containers import AnyContainer

__all__ = ['ErrorBoundary']

initial_value: Optional[Exception] = None

@component
def ErrorBoundary(fallback: Callable[[str, Exception], 'AnyContainer'], 
                 children: Callable[[], 'AnyContainer']) -> 'AnyContainer':
    """
    Componente límite de error que captura excepciones en componentes hijos.
    
    Comportamiento:
        1. Intenta renderizar los componentes hijos
        2. Si ocurre una excepción:
            - Captura el error
            - Almacena el error en el estado del componente
            - Renderiza el componente fallback con el error
        3. En renders posteriores, sigue mostrando el fallback hasta que se resetea
    
    Args:
        fallback: Función que recibe una key y la excepción y retorna un componente UI
        children: Componentes hijos a proteger
        
    Returns:
        - children() si no hay errores
        - fallback(key, exception) si ocurrió un error
        
    Ejemplo de uso:
        @component
        def my_fallback(exc: Exception):
            return Label(text=f"Error: {str(exc)}")
        
        @component
        def protected_content():
            return MyComponent()
        
        ErrorBoundary(fallback=lambda key, exc: my_fallback(None, key, exc=exc), children=protected_content)
    """
    exception, set_exception = use_state(initial_value=initial_value)

    if not exception:
        try:
            return children()

        except Exception as exc:
            set_exception(exc)
            exception = exc
    
    return fallback('fallback', exception)
