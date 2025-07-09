import os
from typing import Dict, Hashable, Iterable, Sequence, Tuple
from pyte import Stream, Screen
from pyte.screens import Char as CharPE
from prompt_toolkit.output.vt100 import Vt100_Output
from prompt_toolkit.data_structures import Size as SizePT
from prompt_toolkit.output import ColorDepth
from prompt_toolkit.styles import ANSI_COLOR_NAMES, Attrs
from prompt_toolkit.utils import is_dumb_terminal

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


FG_ANSI_COLORS = {
    "ansidefault": 39,
    # Low intensity.
    "ansiblack": 30,
    "ansired": 31,
    "ansigreen": 32,
    "ansiyellow": 33,
    "ansiblue": 34,
    "ansimagenta": 35,
    "ansicyan": 36,
    "ansigray": 37,
    # High intensity.
    "ansibrightblack": 90,
    "ansibrightred": 91,
    "ansibrightgreen": 92,
    "ansibrightyellow": 93,
    "ansibrightblue": 94,
    "ansibrightmagenta": 95,
    "ansibrightcyan": 96,
    "ansiwhite": 97,
}

BG_ANSI_COLORS = {
    "ansidefault": 49,
    # Low intensity.
    "ansiblack": 40,
    "ansired": 41,
    "ansigreen": 42,
    "ansiyellow": 43,
    "ansiblue": 44,
    "ansimagenta": 45,
    "ansicyan": 46,
    "ansigray": 47,
    # High intensity.
    "ansibrightblack": 100,
    "ansibrightred": 101,
    "ansibrightgreen": 102,
    "ansibrightyellow": 103,
    "ansibrightblue": 104,
    "ansibrightmagenta": 105,
    "ansibrightcyan": 106,
    "ansiwhite": 107,
}


ANSI_COLORS_TO_RGB = {
    "ansidefault": (
        0x00,
        0x00,
        0x00,
    ),  # Don't use, 'default' doesn't really have a value.
    "ansiblack": (0x00, 0x00, 0x00),
    "ansigray": (0xE5, 0xE5, 0xE5),
    "ansibrightblack": (0x7F, 0x7F, 0x7F),
    "ansiwhite": (0xFF, 0xFF, 0xFF),
    # Low intensity.
    "ansired": (0xCD, 0x00, 0x00),
    "ansigreen": (0x00, 0xCD, 0x00),
    "ansiyellow": (0xCD, 0xCD, 0x00),
    "ansiblue": (0x00, 0x00, 0xCD),
    "ansimagenta": (0xCD, 0x00, 0xCD),
    "ansicyan": (0x00, 0xCD, 0xCD),
    # High intensity.
    "ansibrightred": (0xFF, 0x00, 0x00),
    "ansibrightgreen": (0x00, 0xFF, 0x00),
    "ansibrightyellow": (0xFF, 0xFF, 0x00),
    "ansibrightblue": (0x00, 0x00, 0xFF),
    "ansibrightmagenta": (0xFF, 0x00, 0xFF),
    "ansibrightcyan": (0x00, 0xFF, 0xFF),
}


assert set(FG_ANSI_COLORS) == set(ANSI_COLOR_NAMES)
assert set(BG_ANSI_COLORS) == set(ANSI_COLOR_NAMES)
assert set(ANSI_COLORS_TO_RGB) == set(ANSI_COLOR_NAMES)


def _get_closest_ansi_color(r: int, g: int, b: int, exclude: Sequence[str] = ()) -> str:
    """
    Find closest ANSI color. Return it by name.

    :param r: Red (Between 0 and 255.)
    :param g: Green (Between 0 and 255.)
    :param b: Blue (Between 0 and 255.)
    :param exclude: A tuple of color names to exclude. (E.g. ``('ansired', )``.)
    """
    exclude = list(exclude)

    # When we have a bit of saturation, avoid the gray-like colors, otherwise,
    # too often the distance to the gray color is less.
    saturation = abs(r - g) + abs(g - b) + abs(b - r)  # Between 0..510

    if saturation > 30:
        exclude.extend(["ansilightgray", "ansidarkgray", "ansiwhite", "ansiblack"])

    # Take the closest color.
    # (Thanks to Pygments for this part.)
    distance = 257 * 257 * 3  # "infinity" (>distance from #000000 to #ffffff)
    match = "ansidefault"

    for name, (r2, g2, b2) in ANSI_COLORS_TO_RGB.items():
        if name != "ansidefault" and name not in exclude:
            d = (r - r2) ** 2 + (g - g2) ** 2 + (b - b2) ** 2

            if d < distance:
                match = name
                distance = d

    return match


_ColorCodeAndName = Tuple[int, str]

class _16ColorCache:
    """
    Cache which maps (r, g, b) tuples to 16 ansi colors.

    :param bg: Cache for background colors, instead of foreground.
    """

    def __init__(self, bg: bool = False) -> None:
        self.bg = bg
        self._cache: dict[Hashable, _ColorCodeAndName] = {}

    def get_code(
        self, value: tuple[int, int, int], exclude: Sequence[str] = ()
    ) -> _ColorCodeAndName:
        """
        Return a (ansi_code, ansi_name) tuple. (E.g. ``(44, 'ansiblue')``.) for
        a given (r,g,b) value.
        """
        key: Hashable = (value, tuple(exclude))
        cache = self._cache

        if key not in cache:
            cache[key] = self._get(value, exclude)

        return cache[key]

    def _get(
        self, value: tuple[int, int, int], exclude: Sequence[str] = ()
    ) -> _ColorCodeAndName:
        r, g, b = value
        match = _get_closest_ansi_color(r, g, b, exclude=exclude)

        # Turn color name into code.
        if self.bg:
            code = BG_ANSI_COLORS[match]
        else:
            code = FG_ANSI_COLORS[match]

        return code, match


class _256ColorCache(Dict[Tuple[int, int, int], int]):
    """
    Cache which maps (r, g, b) tuples to 256 colors.
    """

    def __init__(self) -> None:
        # Build color table.
        colors: list[tuple[int, int, int]] = []

        # colors 0..15: 16 basic colors
        colors.append((0x00, 0x00, 0x00))  # 0
        colors.append((0xCD, 0x00, 0x00))  # 1
        colors.append((0x00, 0xCD, 0x00))  # 2
        colors.append((0xCD, 0xCD, 0x00))  # 3
        colors.append((0x00, 0x00, 0xEE))  # 4
        colors.append((0xCD, 0x00, 0xCD))  # 5
        colors.append((0x00, 0xCD, 0xCD))  # 6
        colors.append((0xE5, 0xE5, 0xE5))  # 7
        colors.append((0x7F, 0x7F, 0x7F))  # 8
        colors.append((0xFF, 0x00, 0x00))  # 9
        colors.append((0x00, 0xFF, 0x00))  # 10
        colors.append((0xFF, 0xFF, 0x00))  # 11
        colors.append((0x5C, 0x5C, 0xFF))  # 12
        colors.append((0xFF, 0x00, 0xFF))  # 13
        colors.append((0x00, 0xFF, 0xFF))  # 14
        colors.append((0xFF, 0xFF, 0xFF))  # 15

        # colors 16..232: the 6x6x6 color cube
        valuerange = (0x00, 0x5F, 0x87, 0xAF, 0xD7, 0xFF)

        for i in range(217):
            r = valuerange[(i // 36) % 6]
            g = valuerange[(i // 6) % 6]
            b = valuerange[i % 6]
            colors.append((r, g, b))

        # colors 233..253: grayscale
        for i in range(1, 22):
            v = 8 + i * 10
            colors.append((v, v, v))

        self.colors = colors

    def __missing__(self, value: tuple[int, int, int]) -> int:
        r, g, b = value

        # Find closest color.
        # (Thanks to Pygments for this!)
        distance = 257 * 257 * 3  # "infinity" (>distance from #000000 to #ffffff)
        match = 0

        for i, (r2, g2, b2) in enumerate(self.colors):
            if i >= 16:  # XXX: We ignore the 16 ANSI colors when mapping RGB
                # to the 256 colors, because these highly depend on
                # the color scheme of the terminal.
                d = (r - r2) ** 2 + (g - g2) ** 2 + (b - b2) ** 2

                if d < distance:
                    match = i
                    distance = d

        # Turn color name into code.
        self[value] = match
        return match


_16_fg_colors = _16ColorCache(bg=False)
_16_bg_colors = _16ColorCache(bg=True)
_256_colors = _256ColorCache()

class _EscapeCodeCache(Dict[Attrs, str]):
    """
    Cache for VT100 escape codes. It maps
    (fgcolor, bgcolor, bold, underline, strike, reverse) tuples to VT100
    escape sequences.

    :param true_color: When True, use 24bit colors instead of 256 colors.
    """

    def __init__(self, color_depth: ColorDepth) -> None:
        self.color_depth = color_depth

    def __missing__(self, attrs: Attrs) -> str:
        (
            fgcolor,
            bgcolor,
            bold,
            underline,
            strike,
            italic,
            blink,
            reverse,
            hidden,
        ) = attrs
        parts: list[str] = []

        parts.extend(self._colors_to_code(fgcolor or "", bgcolor or ""))

        if bold:
            parts.append("1")
        if italic:
            parts.append("3")
        if blink:
            parts.append("5")
        if underline:
            parts.append("4")
        if reverse:
            parts.append("7")
        if hidden:
            parts.append("8")
        if strike:
            parts.append("9")

        if parts:
            result = "\x1b[0;" + ";".join(parts) + "m"
        else:
            result = "\x1b[0m"

        self[attrs] = result
        return result

    def _color_name_to_rgb(self, color: str) -> tuple[int, int, int]:
        "Turn 'ffffff', into (0xff, 0xff, 0xff)."
        try:
            rgb = int(color, 16)
        except ValueError:
            raise
        else:
            r = (rgb >> 16) & 0xFF
            g = (rgb >> 8) & 0xFF
            b = rgb & 0xFF
            return r, g, b

    def _colors_to_code(self, fg_color: str, bg_color: str) -> Iterable[str]:
        """
        Return a tuple with the vt100 values  that represent this color.
        """
        # When requesting ANSI colors only, and both fg/bg color were converted
        # to ANSI, ensure that the foreground and background color are not the
        # same. (Unless they were explicitly defined to be the same color.)
        fg_ansi = ""

        def get(color: str, bg: bool) -> list[int]:
            nonlocal fg_ansi

            table = BG_ANSI_COLORS if bg else FG_ANSI_COLORS

            if not color or self.color_depth == ColorDepth.DEPTH_1_BIT:
                return []

            # 16 ANSI colors. (Given by name.)
            elif color in table:
                return [table[color]]

            # RGB colors. (Defined as 'ffffff'.)
            else:
                try:
                    rgb = self._color_name_to_rgb(color)
                except ValueError:
                    return []

                # When only 16 colors are supported, use that.
                if self.color_depth == ColorDepth.DEPTH_4_BIT:
                    if bg:  # Background.
                        if fg_color != bg_color:
                            exclude = [fg_ansi]
                        else:
                            exclude = []
                        code, name = _16_bg_colors.get_code(rgb, exclude=exclude)
                        return [code]
                    else:  # Foreground.
                        code, name = _16_fg_colors.get_code(rgb)
                        fg_ansi = name
                        return [code]

                # True colors. (Only when this feature is enabled.)
                elif self.color_depth == ColorDepth.DEPTH_24_BIT:
                    r, g, b = rgb
                    return [(48 if bg else 38), 2, r, g, b]

                # 256 RGB colors.
                else:
                    return [(48 if bg else 38), 5, _256_colors[rgb]]

        result: list[int] = []
        result.extend(get(fg_color, False))
        result.extend(get(bg_color, True))

        return map(str, result)

class TerminalOutput(Vt100_Output):
    """
    Emulador de terminal para testing de aplicaciones CLI,
    con capacidad para capturar y verificar el estado del terminal.
    """
    def __init__(
                self,
                columns: int = 80,
                rows: int = 24,
                default_color_depth: ColorDepth | None = None,
                term: str | None = None,
                enable_bell: bool = True,
                enable_cpr: bool = False,
            ):
        self.term = term
        self.enable_bell = enable_bell
        self.enable_cpr = enable_cpr
        self.default_color_depth = default_color_depth
        
        self._screen = Screen(columns=columns, lines=rows)
        self._stream = Stream(self._screen)
        self._cursor_visible = None
        self._cursor_shape_changed = False
        
        self._escape_code_caches: dict[ColorDepth, _EscapeCodeCache] = { # type: ignore
            ColorDepth.DEPTH_1_BIT: _EscapeCodeCache(ColorDepth.DEPTH_1_BIT),
            ColorDepth.DEPTH_4_BIT: _EscapeCodeCache(ColorDepth.DEPTH_4_BIT),
            ColorDepth.DEPTH_8_BIT: _EscapeCodeCache(ColorDepth.DEPTH_8_BIT),
            ColorDepth.DEPTH_24_BIT: _EscapeCodeCache(ColorDepth.DEPTH_24_BIT),
        }
    
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

    def fileno(self) -> int:
        return 0
    
    def write_raw(self, data: str) -> None:
        self._stream.feed(data)

    def write(self, data: str) -> None:
        self._stream.feed(data)
        # self._stream.feed(data.replace("\x1b", "?"))

    def flush(self) -> None:
        """Vacía el buffer (no-op)."""
        pass

    def reset(self) -> None:
        """Reinicia el estado del emulador."""
        self._screen.reset()
        self._stream = Stream(self._screen)

    def scroll_buffer_to_prompt(self) -> None:
        pass

    def encoding(self) -> str:
        return 'utf-8'

    def resize(self, rows: int, columns: int):
        self._screen.resize(lines=rows, columns=columns)

    @property
    def responds_to_cpr(self) -> bool:
        if not self.enable_cpr:
            return False

        # When the input is a tty, we assume that CPR is supported.
        # It's not when the input is piped from Pexpect.
        if os.environ.get("PROMPT_TOOLKIT_NO_CPR", "") == "1":
            return False

        return not is_dumb_terminal(self.term)

    def erase_screen(self):
        self.cursor_goto(0, 0)
    
    def erase_end_of_line(self):
        self.cursor_goto(self._screen.cursor.y, 0)

    def erase_down(self):
        self.cursor_goto(self._screen.cursor.y, 0)
