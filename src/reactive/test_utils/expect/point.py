from typing import Generator, Self, TYPE_CHECKING
from dataclasses import dataclass

from ...data_structures import Box, Char, Point, Size, Style
from .utils import get_size_text
from .style import StyleBase
from .desplace import DesplaceBase
from .text import ExpectText

if TYPE_CHECKING:
    from .expect import Expect

__all__ = ['ExpectPoint']

@dataclass
class ExpectPoint(StyleBase, DesplaceBase):
    _expect: 'Expect'
    _box: 'Box'

    @classmethod
    def from_point(cls, expect: 'Expect', point: 'Point') -> Self:
        box = Box(point, size=Size.one())
        cls._validate_box(box=box, expect=expect)
        return cls(_expect=expect, _box=box)
    
    @classmethod
    def from_position(cls, expect: 'Expect', row: int, column: int) -> Self:
        box = Box.from_position_and_size(row=row, column=column, rows=1, columns=1)
        cls._validate_box(box=box, expect=expect)
        return cls(_expect=expect, _box=box)
    
    @staticmethod
    def _validate_box(box: 'Box', expect: 'Expect') -> None:
        assert box in expect.box

    @property
    def point(self) -> 'Point':
        return self._box.point

    @property
    def box(self) -> 'Box':
        return self._box
    
    @property
    def char(self) -> str:
        return self.char
    
    @property
    def style(self) -> 'Style':
        return self._expect.terminal.get_char(row=self.point.row, column=self.point.column).style

    def cursor(self) -> Self:
        """Asegura que el cursor este en esta posicion"""
        assert self._expect.terminal.cursor() == self.point
        return self

    def not_cursor(self) -> Self:
        assert self._expect.terminal.cursor() != self.point
        return self

    def row(self) -> 'ExpectText':
        box = Box(
            point = Point(row=self.point.row, column=0),
            size=Size(columns=self._expect.size.columns, rows=1)
        )
        return ExpectText.from_box(expect=self._expect, box=box)

    def text(self, text: str) -> 'ExpectText':
        """Asegura que el texto se encuentre a partir de esta posicion"""
        size = get_size_text(text=text)
        box = Box(size=size, point=self.point)
        return ExpectText.from_box(box=box, expect=self._expect).equal(text)

    def not_text(self, text: str) -> Self:
        size = get_size_text(text=text)
        box = Box(size=size, point=self.point)
        ExpectText.from_box(box=box, expect=self._expect).not_equal(text)
        return self

    def _get_text(self) -> str:
        return self._expect.terminal.get_char(row=self.point.row, column=self.point.column).data

    def _iter_chars(self) -> Generator[tuple['Point', 'Char']]:
        char = self._expect.terminal.get_char(row=self.point.row, column=self.point.column)
        yield self.point, char
