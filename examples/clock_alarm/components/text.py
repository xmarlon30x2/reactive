from typing import TYPE_CHECKING

from reactive import component
from prompt_toolkit.layout.containers import Window
from prompt_toolkit.layout.controls import FormattedTextControl

if TYPE_CHECKING:
    from prompt_toolkit.formatted_text import AnyFormattedText

__all__ = ['Text']

@component
def Text(text: 'AnyFormattedText', focusable: bool = False):
    return Window(FormattedTextControl(text=text, focusable=focusable))
