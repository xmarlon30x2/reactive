from dataclasses import dataclass
from typing import Generator, Pattern, Self, overload, TYPE_CHECKING
import re

from .utils import find_box

from ...data_structures import Box, Char, Point, Size
from .utils import get_text_from_rect
from .desplace import DesplaceBase
from .style import StyleBase

if TYPE_CHECKING:
    from .expect import Expect

__all__ = ['ExpectText']

@dataclass
class ExpectText(StyleBase, DesplaceBase):
    _expect: 'Expect'
    _box: 'Box'
    
    @classmethod
    def from_box(cls, expect: 'Expect', box: Box) -> Self:
        cls._validate_box(box=box, expect=expect)
        return cls(_expect=expect, _box=box)

    @classmethod
    def from_position_and_size(cls, expect: 'Expect', row: int, column: int, rows: int, columns: int) -> Self:
        box = Box.from_position_and_size(row=row, column=column, rows=rows, columns=columns)
        cls._validate_box(box=box, expect=expect)
        return cls(_box=box, _expect=expect)
    
    @staticmethod
    def _validate_box(box: 'Box', expect: 'Expect') -> None:
        assert box in expect.box

    @property
    def box(self) -> 'Box':
        return self._box
    
    @property
    def size(self) -> 'Size':
        return self._box.size
    
    @property
    def point(self) -> 'Point':
        return self._box.point

    @property
    def text(self) -> str:
        rect = self._expect.terminal.get_rect(box=self.box)
        return get_text_from_rect(rect)

    def equal(self, text: str) -> Self:
        """Asegura que el texto sea igual a otro"""
        assert self.text == text, f'Expected text to equal "{text}", but got "{self.text}"'
        return self

    def not_equal(self, text: str) -> Self:
        """Asegura que el texto sea distinto"""
        assert self.text != text, f'Expected text to not be equal to "{text}", but got "{self.text}"'
        return self

    def find(self, query: str) -> 'ExpectText':
        box = find_box(text=self.text, query=query)
        assert box, f'Expected text to contain "{query}", but got "{self.text}"'
        return ExpectText.from_box(expect=self._expect, box=box)

    def contains(self, *texts: str) -> Self:
        """Asegura que la fila no contiene un texto"""
        not_contains = [text for text in texts if text not in texts]
        not_contains_string = '"'+'", "'.join(not_contains)+'"'
        assert not not_contains, f'Expected text to contain {not_contains_string}, but got "{self.text}"'
        return self

    def not_contains(self, *texts: str) -> Self:
        """Asegura que la fila contiene un texto"""
        not_contains = [text for text in texts if text in texts]
        not_contains_string = '"'+'", "'.join(not_contains)+'"'
        assert not not_contains, f'Expected text to not contain {not_contains_string}, but got "{self.text}"'
        return self

    def startswith(self, text: str) -> Self:
        """Asegura que la fila comienze con un texto"""
        assert self.text.startswith(text), f'Expected text to start with "{text}", but got "{self.text}"'
        return self

    def endswith(self, text: str) -> Self:
        """Asegura que la fila termine con un texto"""
        assert self.text.endswith(text), f'Expected text to end with "{text}", but got "{self.text}"'
        return self

    def count(self, text: str, n: int) -> Self:
        occurrences = self.text.count(text)
        assert occurrences == n, f'En el text se esperaban {n} occurrences in "{text}", but got "{occurrences}"'
        return self

    def match(self, regex: str | Pattern[str]) -> Self:
        if isinstance(regex, str):
            regex = re.compile(regex)
        assert regex.search(self.text), f'Expected area to match regex "{regex.pattern}", but got "{self.text}"'
        return self

    def not_match(self, regex: str | Pattern[str]) -> Self:
        if isinstance(regex, str):
            regex = re.compile(regex)
        assert not regex.search(self.text), f'Expected area to not match regex "{regex.pattern}", but got "{self.text}"'
        return self

    @overload
    def subarea(self,
                *,
                row: int,
                column: int,
                rows: int | None = None,
                columns: int | None = None,
            ) -> 'ExpectText': ...
    
    @overload
    def subarea(self, *, box: Box) -> 'ExpectText': ...

    def subarea(self,
                *,
                row: int | None = None,
                column: int | None = None,
                rows: int | None = None,
                columns: int | None = None,
                box: 'Box | None' = None
            ) -> 'ExpectText':
        """Devuelve una parte del texto"""
        if box:
            point = self.point + box.point
            box = Box(point=point, size=box.size)
            assert box in self.box
            return ExpectText.from_box(expect=self._expect, box=box)

        elif row is not None and column is not None:
            rows = rows or self.size.rows - row
            columns = columns or self.size.columns - column
            box = Box.from_position_and_size(column=column, columns=columns, row=row, rows=rows)
            assert box in self.box
            return ExpectText.from_box(expect=self._expect, box=box)
        
        raise ValueError()
    
    @overload
    def at(self, *, row: int, column: int) -> Self: ...
    
    @overload
    def at(self, *, row: int) -> Self: ...
    
    @overload
    def at(self, *, column: int) -> Self: ...
    
    @overload
    def at(self, *, point: 'Point') -> Self: ...

    def at(self,
                *,
                row: int | None = None,
                column: int | None = None,
                point: 'Point | None' = None
            ) -> Self:
        """Asegura que se encuentre en una posicion"""
        if row is not None and column is not None:
            point = Point(row=row, column=column)
        elif row is not None:
            point = Point(row=row, column=self.point.column)
        elif column is not None:
            point = Point(column=column, row=self.point.row)    
        elif point is not None:
            pass
        else:
            raise ValueError()
        assert point == self.point, f'Se esperaba que el texto estubiera en la posicion {point}, pero esta en {self.point}'
        return self

    def row(self, row: int) -> 'ExpectText':
        """Devuelve una columna"""
        assert self.box.size.rows > row >= 0
        box = Box(
            point = Point(row=row, column=self.box.point.column),
            size=self.box.size
        )
        return ExpectText.from_box(expect=self._expect, box=box)

    def below(self, rows: int | None = None) -> 'ExpectText':
        """Debuelve el area de abajo"""
        row = self.size.rows + self.point.row
        rows = rows or self._expect.size.rows - row
        assert rows >= 1
        return ExpectText.from_position_and_size(
            expect=self._expect,
            column=self.point.column,
            columns=self.size.columns,
            row=row,
            rows=rows,
        )

    def above(self, rows: int | None = None) -> 'ExpectText':
        """Debuelve el area de arriba"""
        rows = rows or self.point.row
        assert rows >= 1
        row = self.point.row - rows
        return ExpectText.from_position_and_size(
            expect=self._expect,
            column=self.point.column,
            columns=self.size.columns,
            row=row,
            rows=rows,
        )

    def back(self, columns: int | None = None) -> 'ExpectText':
        """Debuelve el area de atras"""
        columns = columns or self.point.column
        assert columns >= 1
        column = self.point.column - columns
        return ExpectText.from_position_and_size(
            expect=self._expect,
            row=self.point.row,
            rows=self.size.rows,
            column=column,
            columns=columns,
        )

    def forward(self, columns: int | None = None) -> 'ExpectText':
        """Debuelve el area de adelante"""
        column = self.size.columns + self.point.column
        columns = columns or self._expect.size.columns - column
        assert columns >= 1
        return ExpectText.from_position_and_size(
            expect=self._expect,
            row=self.point.row,
            rows=self.size.rows,
            column=column,
            columns=columns,
        )

    def _iter_chars(self) -> Generator[tuple['Point', 'Char']]:
        rect = self._expect.terminal.get_rect(box=self.box)
        for row, columns in enumerate(rect):
            for column, char in enumerate(columns):
                yield Point(row=row, column=column), char
