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
