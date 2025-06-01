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
    if not disable and normal:
        return normal
    if not disable and not normal:
        return default_normal
    if isinstance(disabled, str):
        return disabled
    if disabled == None:
        return default_disabled
    if disabled == False and normal:
        return normal
    return default_normal

def calculate_width(width: Optional[int | Literal['auto']], text_lenght: int):
    if width is None:
        return min(MAX_SIZE, text_lenght)
    if width == 'auto':
        return text_lenght
    return width

@component
def Button(
        text: Optional[str] = None,
        handler: Optional[Callable[[], Any]] = None,
        width: Optional[Union[int, Literal['auto']]] = None,
        disable: bool = False,
        left_symbol: Optional[str] = None,
        left_symbol_disabled: Optional[Union[str, Literal[False]]] = None,
        right_symbol: Optional[str] = None,
        right_symbol_disabled: Optional[Union[str, Literal[False]]] = None
    ):
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
    return _Button(
        text=text,
        handler=handler if not disable else None,
        width=calculate_width(width, len(text)),
        left_symbol=left_symbol,
        right_symbol=right_symbol
    )
