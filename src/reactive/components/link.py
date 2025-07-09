from typing import Any, Callable, Literal

from ..hooks.use_navigation import use_navigation
from .button import Button
from .component import component

__all__ = ['Link']

@component
def Link(
        text: str,
        to: int | str,
        params: dict[str, Any] | None = None,
        handler: Callable[[], None] | None = None,
        disable: bool = False,
        left_symbol: str | None = None,
        right_symbol: str | None = None,
        width: int | Literal['auto'] | None = 'auto',
        left_symbol_disabled: str | None | Literal[False] = None,
        right_symbol_disabled: str | None | Literal[False] = None
    ):
    """
    Componente Link para navegación declarativa.
    
    Args:
        text: Texto a mostrar
        to: Destino (string para ruta o entero para movimiento en historial)
        params: Parámetros para la nueva ruta (si to es string)
        handler: Función adicional a ejecutar antes de navegar
        disable: Deshabilita el enlace
        left_symbol: Símbolo izquierdo personalizado
        right_symbol: Símbolo derecho personalizado
        width: Ancho del enlace (similar a Button)
        left_symbol_disabled: Símbolo izquierdo en estado deshabilitado
        right_symbol_disabled: Símbolo derecho en estado deshabilitado
        
    Returns:
        Componente Button configurado como enlace de navegación
    """
    navigation = use_navigation()
    
    def on_handler():
        if handler:
            handler()
        if isinstance(to, str):
            navigation.link(to, params)
        else:
            navigation.to(to)
    
    return Button(
        text=text,
        handler=on_handler,
        disable=disable,
        width=width,
        left_symbol=left_symbol,
        right_symbol=right_symbol,
        left_symbol_disabled=left_symbol_disabled,
        right_symbol_disabled=right_symbol_disabled
    )
