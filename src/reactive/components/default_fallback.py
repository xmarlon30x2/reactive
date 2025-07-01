from traceback import format_exception
from prompt_toolkit.layout import ScrollablePane, Window
from prompt_toolkit.widgets import Frame
from prompt_toolkit.layout.controls import FormattedTextControl
from prompt_toolkit.formatted_text.pygments import PygmentsTokens
from prompt_toolkit.key_binding import KeyBindings, KeyPressEvent
from prompt_toolkit.key_binding.bindings.scroll import (
    scroll_one_line_up, scroll_one_line_down,
    scroll_page_down, scroll_page_up
)
from pygments import lex # type: ignore
from pygments.lexers.python import PythonTracebackLexer # type: ignore

from ..hooks.use_memo import use_memo # type: ignore

from ..types import Node
from .component import component

__all__ = ['DefaultFallback']

def exception_to_formated_text(exception: 'Exception'):
    tb_lines = format_exception(type(exception), exception, exception.__traceback__)
    tb_text = ''.join(tb_lines)
    
    tokens = lex(tb_text, lexer=PythonTracebackLexer())
    return PygmentsTokens(tokens) # type: ignore

@component
def DefaultFallback(exception: Exception) -> 'Node':
    """
    Componente predeterminado para mostrar excepciones con formato mejorado.
    
    Características:
        - Muestra el traceback completo con resaltado de sintaxis
        - Panel desplazable con controles de teclado (flechas arriba/abajo)
        - Título dinámico con el nombre de la excepción
        - Diseño responsivo que se adapta al tamaño del terminal
        
    Args:
        exception: Excepción a mostrar
        
    Returns:
        Componente con el error formateado
        
    Ejemplo de uso:
        ErrorBoundary(fallback=lambda key, exc: DefaultFallback(None, key, exception=exc), children=lambda: mi_componente())
    """
    kb = KeyBindings()

    @kb.add('up')
    def _(event: 'KeyPressEvent'):
        scroll_one_line_up(event)
    
    @kb.add('down')
    def _(event: 'KeyPressEvent'):
        scroll_one_line_down(event)
    
    @kb.add('pageup')
    def _(event: 'KeyPressEvent'):
        scroll_page_up(event)

    @kb.add('pagedown')
    def _(event: 'KeyPressEvent'):
        scroll_page_down(event)
    
    text_formated = use_memo(lambda: exception_to_formated_text(exception), exception)
    return Frame(
        title=f"Error: {type(exception).__name__}",
        body=ScrollablePane(
            Window(
                FormattedTextControl(
                    text_formated,
                    focusable=True,
                    key_bindings=kb
                )
            )
        )
    )
