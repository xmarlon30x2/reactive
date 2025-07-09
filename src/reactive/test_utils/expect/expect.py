from dataclasses import dataclass
from typing import overload

from ...data_structures import Box, Point, Size
from .utils import get_text_from_rect
from .utils import find_box
from .point import ExpectPoint
from .text import ExpectText
from .terminal import Terminal

@dataclass
class Expect:
    _terminal: Terminal
    
    @property
    def size(self) -> 'Size':
        return self._terminal.get_size()
    
    @property
    def box(self) -> 'Box':
        return Box(size=self._terminal.get_size(), point=Point.zero())

    @property
    def screen(self) -> str:
        rect = self._terminal.get_rect(point=Point.zero(), size=self.size)
        return get_text_from_rect(rect)

    @property
    def terminal(self) -> 'Terminal':
        return self._terminal

    def find(self, query: str | list[str]) -> 'ExpectText':
        """Busca un texto"""
        box = find_box(text=self.screen, query=query)
        assert box, f'No se encontro el texto "{query}" en la pantalla\nScreen:\n"{self.screen}"'
        return ExpectText.from_box(expect=self, box=box)
    
    @overload
    def at(self, *, row: int, column: int) -> 'ExpectPoint': ...
    @overload
    def at(self, *, point: "Point") -> 'ExpectPoint': ...

    def at(self, *, row: int | None = None, column: int | None = None, point: "Point | None" = None) -> 'ExpectPoint':
        """Devuelve una posicion"""
        point = point if point else Point(row=row, column=column) if column and row else Point.zero() 
        if point:
            return ExpectPoint.from_point(expect=self, point=point)
        
        elif column is not None and row is not None:
            return ExpectPoint.from_position(expect=self, row=row, column=column)
        
        raise ValueError()

    @overload
    def area(self,
                *,
                row: int,
                column: int,
                rows: int | None = None,
                columns: int | None = None,
            ) -> 'ExpectText': ...
    @overload
    def area(self, *, box: Box) -> 'ExpectText': ...

    def area(self,
                *,
                row: int | None = None,
                column: int | None = None,
                rows: int | None = None,
                columns: int | None = None,
                box: 'Box | None' = None
            ) -> 'ExpectText':
        """Devuelve un area"""
        if box:
            return ExpectText.from_box(expect=self, box=box)

        elif row and column:
            rows = rows or self.size.rows - row
            columns = columns or self.size.columns - column
            return ExpectText.from_position_and_size(expect=self, row=row, column=column, rows=rows, columns=columns)
        
        raise ValueError()

    def row(self, row: int) -> 'ExpectText':
        """Devuelve una fila"""
        return ExpectText.from_position_and_size(
            expect=self,
            row=row,
            column=0,
            rows=1,
            columns=self.size.columns
        )

    def cursor(self) -> "ExpectPoint":
        """Devuelve el cursor"""
        return ExpectPoint.from_point(self, self.terminal.cursor())

# expect = Expect(...)

# expect.row(3).contains('Next')
# expect.row(4).contains('Exit')
# expect.row(6).contains('Created by team react').underline().color('gray')

# text_hello = expect.find('Hello').at(row=0, column=3)
# text_hello.down().text('World')
# text_hello.down(2).not_text('World')

# text_world = expect.at(row=1, column=3).text('World').bold()

# below_text_world = text_world.below().contains('Next', 'Exit')
# below_text_world.find('Next').color('green').left(2).text('<')
# below_text_world.find('Exit').color('red').right(2).text('>')
