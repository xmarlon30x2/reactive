from typing import Any, Callable, Literal, Optional, Union
from prompt_toolkit.widgets.base import Button as _Button

from .component import component

__all__ = ['Button']

DEFAULT_TEXT = 'button'
LEFT_SYMBOL_DISABLED = '('
RIGHT_SYMBOL_DISABLED = ')'
LEFT_SYMBOL = '<'
RIGHT_SYMBOL = '>'
MAX_SIZE = 30

def get_symbol(
        normal: Optional[str],
        default_normal: str,
        disabled: Optional[str | Literal[False]],
        default_disabled: str,
        disable: bool
    ) -> str:
    """
    Determina el símbolo a mostrar según el estado del botón (normal/deshabilitado).
    
    Args:
        normal: Símbolo personalizado para estado normal
        default_normal: Símbolo predeterminado para estado normal
        disabled: Símbolo personalizado para estado deshabilitado
        default_disabled: Símbolo predeterminado para estado deshabilitado
        disable: Estado actual del botón
        
    Returns:
        Símbolo seleccionado según las reglas de prioridad
    """
    if not disable and normal:
        return normal
    if not disable and not normal:
        return default_normal
    if isinstance(disabled, str):
        return disabled
    if disabled is None:
        return default_disabled
    return default_normal

def calculate_width(
        width: Optional[int | Literal['auto']],
        text_lenght: int,
        left_width: int,
        right_width: int,
    ):
    """
    Calcula el ancho del botón según diferentes estrategias.
    
    Args:
        width: Especificación de ancho (número fijo, 'auto', o None)
        text_lenght: Longitud del texto del botón
        left_width: Ancho del símbolo izquierdo
        right_width: Ancho del símbolo derecho
        
    Returns:
        Ancho calculado para el botón
    """
    if width is None:
        return min(MAX_SIZE, text_lenght)
    if width == 'auto':
        return text_lenght + left_width + right_width
    return width

@component
def Button(
        text: Optional[str] = None,
        handler: Optional[Callable[[], Any]] = None,
        width: Optional[Union[int, Literal['auto']]] = 'auto',
        disable: bool = False,
        left_symbol: Optional[str] = None,
        left_symbol_disabled: Optional[Union[str, Literal[False]]] = None,
        right_symbol: Optional[str] = None,
        right_symbol_disabled: Optional[Union[str, Literal[False]]] = None
    ):
    """
    Componente Button personalizado para interfaces CLI.
    
    Args:
        text: Texto a mostrar en el botón
        handler: Función a ejecutar al presionar el botón
        width: Ancho del botón ('auto', entero, o None para máximo 30)
        disable: Deshabilita el botón si es True
        left_symbol: Símbolo izquierdo personalizado (estado normal)
        left_symbol_disabled: Símbolo izquierdo personalizado (estado deshabilitado)
        right_symbol: Símbolo derecho personalizado (estado normal)
        right_symbol_disabled: Símbolo derecho personalizado (estado deshabilitado)
        
    Returns:
        Componente Button de Prompt Toolkit configurado
    """
    text = text or DEFAULT_TEXT
    left_symbol = get_symbol(
        normal=left_symbol,
        default_normal=LEFT_SYMBOL,
        disabled=left_symbol_disabled,
        default_disabled=LEFT_SYMBOL_DISABLED,
        disable=disable
    )
    right_symbol = get_symbol(
        normal=right_symbol,
        default_normal=RIGHT_SYMBOL,
        disabled=right_symbol_disabled,
        default_disabled=RIGHT_SYMBOL_DISABLED,
        disable=disable
    )
    left_width = len(left_symbol)
    right_width = len(right_symbol)
    calcuated_width = calculate_width(width, len(text), left_width, right_width)
    text_size = calcuated_width - (left_width + right_width)
    return _Button(
        text=text if len(text) <= text_size else text[:text_size],
        handler=handler if not disable else None,
        width=calcuated_width,
        left_symbol=left_symbol,
        right_symbol=right_symbol
    )
