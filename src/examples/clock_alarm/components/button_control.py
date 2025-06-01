from typing import Callable

from reactive import component
from prompt_toolkit.widgets import Button

__all__ = ['ButtonControl']

@component
def ButtonControl(text: str, action: Callable[[], None], disabled: bool = False):
    return Button(
        text=text,
        handler=action if disabled else lambda: None,
        left_symbol='[' if not disabled else '(',
        right_symbol=']' if not disabled else ')'
    )
