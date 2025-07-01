from abc import abstractmethod
from typing import Generator, Self, overload
from ...data_structures import Style, Char, Point

__all__ = ['StyleBase']

def _default_value[V](value: V | None, default: V) -> V:
    if value is None:
        return default
    return value

class StyleBase:
    @abstractmethod
    def _get_text(self) -> str: ...

    @abstractmethod
    def _iter_chars(self) -> Generator[tuple['Point', 'Char']]: ...

    def bold(self, value: bool | None = True) -> Self:
        """Asegura que el texto esta en negrita"""
        for point, style in self._iter_styles():
            assert _default_value(style.bold, False) == _default_value(value, False), f'Se esperaba que todo el texto "{self._get_text()}" tuviera el el bold="{value}", pero la posicion {point} tiene "{style.bold}"'

        return self

    def color(self, value: str | None = None) -> Self:
        """Asegura que el texto tiene un color"""
        for point, style in self._iter_styles():
            assert _default_value(style.color, None) == _default_value(value, None), f'Se esperaba que todo el texto "{self._get_text()}" tuviera el color="{value}", pero la posicion {point} tiene "{style.color}"'

        return self

    def bgcolor(self, value: str | None = None) -> Self:
        """Asegura que el texto tiene un color de fondo"""
        for point, style in self._iter_styles():
            assert _default_value(style.bgcolor, None) == _default_value(value, None), f'Se esperaba que todo el texto "{self._get_text()}" tuviera el bgcolor="{value}", pero la posicion {point} tiene "{style.bgcolor}"'

        return self
    
    def blink(self, value: bool | None = None) -> Self:
        for point, style in self._iter_styles():
            assert _default_value(style.blink, False) == _default_value(value, False), f'Se esperaba que todo el texto "{self._get_text()}" tuviera el blink="{value}", pero la posicion {point} tiene "{style.blink}"'

        return self
    
    def italic(self, value: bool | None = None) -> Self:
        for point, style in self._iter_styles():
            assert _default_value(style.italic, False) == _default_value(value, False), f'Se esperaba que todo el texto "{self._get_text()}" tuviera el italic="{value}", pero la posicion {point} tiene "{style.italic}"'

        return self
    
    def reverse(self, value: bool | None = None) -> Self:
        for point, style in self._iter_styles():
            assert _default_value(style.reverse, False) == _default_value(value, False), f'Se esperaba que todo el texto "{self._get_text()}" tuviera el reverse="{value}", pero la posicion {point} tiene "{style.reverse}"'

        return self
    
    def strike(self, value: bool | None = None) -> Self:
        for point, style in self._iter_styles():
            assert _default_value(style.strike, False) == _default_value(value, False), f'Se esperaba que todo el texto "{self._get_text()}" tuviera el strike="{value}", pero la posicion {point} tiene "{style.strike}"'

        return self
    
    def underline(self, value: bool | None = None) -> Self:
        for point, style in self._iter_styles():
            assert _default_value(style.underline, False) == _default_value(value, False), f'Se esperaba que todo el texto "{self._get_text()}" tuviera el underline="{value}", pero la posicion {point} tiene "{style.underline}"'

        return self
    
    def hidden(self, value: bool | None = None) -> Self:
        for point, style in self._iter_styles():
            assert _default_value(style.hidden, False) == _default_value(value, False), f'Se esperaba que todo el texto "{self._get_text()}" tuviera el hidden="{value}", pero la posicion {point} tiene "{style.hidden}"'

        return self

    @overload
    def styled(self,
               *,
                color: str | None = None,
                bgcolor: str | None = None,
                bold: bool | None = None,
                underline: bool | None = None,
                strike: bool | None = None,
                italic: bool | None = None,
                blink: bool | None = None,
                reverse: bool | None = None,
                hidden: bool | None = None,
            ) -> Self: ...
    @overload
    def styled(self,
               *,
               style: 'Style'
               ) -> Self: ...
    def styled(self,
               *,
                color: str | None = None,
                bgcolor: str | None = None,
                bold: bool | None = None,
                underline: bool | None = None,
                strike: bool | None = None,
                italic: bool | None = None,
                blink: bool | None = None,
                reverse: bool | None = None,
                hidden: bool | None = None,
                style: 'Style | None' = None
            ) -> Self:
        """Asegura que el texto tiene los estilos"""
        style = style if style else Style(
            color=color,
            bgcolor=bgcolor,
            bold=bold,
            underline=underline,
            strike=strike,
            blink=blink,
            hidden=hidden,
            italic=italic,
            reverse=reverse
        )
        return (
            self.color(style.color)
            .bgcolor(style.bgcolor).bold(style.bold)
            .underline(style.underline).strike(style.strike)
            .italic(style.italic).blink(style.blink)
            .reverse(style.reverse).hidden(style.hidden)
        )

    def _iter_styles(self):
        for point, char in self._iter_chars():
            yield point, char.style
