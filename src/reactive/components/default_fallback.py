from traceback import format_exception

from prompt_toolkit.widgets import Frame
from prompt_toolkit.layout import ScrollablePane, Window, FormattedTextControl, HSplit
from prompt_toolkit.key_binding.bindings.scroll import scroll_one_line_up, scroll_one_line_down
from prompt_toolkit.key_binding.key_bindings import KeyBindings
from prompt_toolkit.formatted_text import PygmentsTokens
from prompt_toolkit.styles import style_from_pygments_cls
from pygments.lexers.python import PythonTracebackLexer # type: ignore
from pygments import lex # type: ignore
from pygments.styles.onedark import OneDarkStyle # type: ignore

from .component import component

__all__ = ['DefaultFallback']

style = style_from_pygments_cls(OneDarkStyle)
python_traceback_lexer = PythonTracebackLexer()

kb = KeyBindings()
kb.add('up')(scroll_one_line_up)
kb.add('down')(scroll_one_line_down)

@component
def DefaultFallback(exception: Exception):
    traceback = '\n'.join(format_exception(
        type(exception), exception, exception.__traceback__))
    formatted = PygmentsTokens(list(lex(traceback, python_traceback_lexer)))

    return Frame(
        ScrollablePane(
            HSplit([
                Window(FormattedTextControl(
                    formatted,
                    focusable=True,
                    show_cursor=True,
                    key_bindings=kb
                ))
            ])
        )
    )
