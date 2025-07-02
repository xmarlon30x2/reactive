from prompt_toolkit.cursor_shapes import CursorShape
from pyte import Stream, Screen
from pyte.modes import LNM, DECAWM
from pyte.screens import Char as CharPE
from prompt_toolkit.output import Output
from prompt_toolkit.data_structures import Size as SizePT
from prompt_toolkit.styles import Attrs
from prompt_toolkit.output import ColorDepth

from ..data_structures import Char, Point, Size, Style
from .expect.terminal import Terminal

def _map_char(char: CharPE):
    style = Style(
        bgcolor=char.bg,
        bold=char.bold,
        color=char.fg,
        underline=char.underscore,
        strike=char.strikethrough,
        italic=char.italics,
        blink=char.blink,
        reverse=char.reverse,
        hidden=None,
    )
    return Char(data=char.data, style=style)

class TerminalOutput(Output):
    """
    Emulador de terminal para testing de aplicaciones CLI,
    con capacidad para capturar y verificar el estado del terminal.
    """
    def __init__(self, columns: int = 80, rows: int = 24):
        self._screen = Screen(columns=columns, lines=rows)
        self._stream = Stream(self._screen)
        self._data_buffer: list[str] = []
        self._mouse_support_enabled = False
        self._alternate_screen_active = False
    
    def capture(self) -> 'Terminal':
        display = tuple(map(
            lambda row: tuple(map(
                    _map_char,
                    row.values()
                )),
            self._screen.buffer.values()
        ))
        size = Size(rows=self._screen.lines, columns=self._screen.columns)
        cursor=Point(row=self._screen.cursor.y, column=self._screen.cursor.x)

        return Terminal(
            _display=display,
            _size=size,
            _cursor=cursor,
            _cursor_hidden=self._screen.cursor.hidden,
            _title=self._screen.title
        )

    def get_rows_below_cursor_position(self) -> int:
        return self._screen.lines - self._screen.cursor.y - 1

    def get_size(self) -> 'SizePT':
        return SizePT(columns=self._screen.columns, rows=self._screen.lines)

    def write(self, data: str) -> None:
        # data = escape(data)
        self._data_buffer.append(data)
        self._stream.feed(data)

    def flush(self) -> None:
        """Vacía el buffer (no-op)."""
        pass

    def set_title(self, title: str) -> None:
        """Establece el título de la ventana."""
        self._screen.set_title(title)

    def clear_title(self) -> None:
        self._screen.set_title("")

    def erase_screen(self) -> None:
        # self._screen.erase_in_display(2)
        self.cursor_goto(0, 0)

    def enter_alternate_screen(self) -> None:
        if not self._alternate_screen_active:
            self._screen.set_mode(LNM)
            self._alternate_screen_active = True

    def quit_alternate_screen(self) -> None:
        if self._alternate_screen_active:
            self._screen.reset_mode(LNM)
            self._alternate_screen_active = False

    def enable_mouse_support(self) -> None:
        self._mouse_support_enabled = True

    def disable_mouse_support(self) -> None:
        self._mouse_support_enabled = False

    def get_default_color_depth(self) -> 'ColorDepth':
        return ColorDepth.DEPTH_24_BIT

    def reset(self) -> None:
        """Reinicia el estado del emulador."""
        self._screen.reset()
        self._stream = Stream(self._screen)
        self._data_buffer = []
        self._mouse_support_enabled = False
        self._alternate_screen_active = False

    def erase_down(self) -> None:
        # self.cursor_goto(self._screen.cursor.y + 1, self._screen.cursor.x)
        # self._screen.erase_in_display(0)
        # self.cursor_goto(0, 0)
        pass

    def erase_end_of_line(self) -> None:
        self._screen.erase_in_line(0)
        self.cursor_goto(0, 0)

    def reset_attributes(self) -> None:
        self._screen.select_graphic_rendition(0)
        self._screen.cursor.attrs = CharPE(data=self._screen.cursor.attrs.data)

    def set_attributes(self, attrs: 'Attrs', color_depth: 'ColorDepth') -> None:
        """Configura los atributos de texto actuales."""
        char = CharPE(
            data=self._screen.cursor.attrs.data,
            bold=attrs.bold or False,
            italics=attrs.italic or False,
            underscore=attrs.underline or False,
            blink=attrs.blink or False,
            reverse=attrs.reverse or False,
            strikethrough=attrs.strike or False,
            bg=attrs.bgcolor or 'default',
            fg=attrs.color or 'default',
        )
        self._screen.cursor.hidden = attrs.hidden or False
        self._screen.cursor.attrs = char

    def disable_autowrap(self) -> None:
        self._screen.reset_mode(DECAWM)

    def enable_autowrap(self) -> None:
        self._screen.set_mode(DECAWM)

    def cursor_goto(self, row: int = 0, column: int = 0) -> None:
        self._screen.cursor_position(row, column)

    def cursor_up(self, amount: int) -> None:
        self._screen.cursor_up(amount)

    def cursor_down(self, amount: int) -> None:
        self._screen.cursor_down(amount)

    def cursor_forward(self, amount: int) -> None:
        self._screen.cursor_forward(amount)

    def cursor_backward(self, amount: int) -> None:
        self._screen.cursor_back(amount)

    def hide_cursor(self) -> None:
        self._screen.cursor.hidden = True

    def show_cursor(self) -> None:
        self._screen.cursor.hidden = False

    def scroll_buffer_to_prompt(self) -> None:
        pass

    def ask_for_cpr(self) -> None:
        pass

    def bell(self) -> None:
        self._screen.bell()

    def fileno(self) -> int:
        return 0

    def encoding(self) -> str:
        return 'utf-8'

    def write_raw(self, data: str) -> None:
        self._data_buffer.append(data)
        self._stream.feed(data)

    def set_cursor_shape(self, cursor_shape: 'CursorShape') -> None:
        pass

    def reset_cursor_shape(self) -> None:
        pass

    def resize(self, rows: int, columns: int):
        self._screen.resize(lines=rows, columns=columns)
