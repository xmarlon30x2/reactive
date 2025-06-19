from dataclasses import dataclass
from typing import overload

from ...data_structures import Box, Char, Size, Point

__all__ = ['Terminal']

@dataclass
class Terminal:
    _display: tuple[tuple['Char', ...], ...]
    _size: Size
    _cursor: Point
    _cursor_hidden: bool
    _title: str

    def get_size(self) -> Size:
        return self._size

    def cursor(self) -> Point:
        return self._cursor

    def get_title(self) -> str | None:
        return self._title

    def get_char(self, row: int, column: int) -> 'Char':
        try:
            return self._display[row][column]
        except IndexError:
            return Char.space()
    
    @overload
    def get_rect(self, *, row: int, column: int, rows: int, columns: int) -> list[list[Char]]: ...
    
    @overload
    def get_rect(self, *, point: 'Point', size: 'Size') -> list[list[Char]]: ...

    @overload
    def get_rect(self, *, box: 'Box') -> list[list[Char]]: ...

    def get_rect(
            self,
            row: int | None = None,
            column: int | None = None,
            rows: int | None = None,
            columns: int | None = None,
            point: 'Point | None' = None,
            size: 'Size | None' = None,
            box: 'Box | None' = None
        ):
        if box and not (size and point):
            size = box.size
            point = box.point
        row, column = (row, column) if row and column else point or (0, 0)
        rows, columns = (rows, columns) if rows and columns else size or (0, 0)
        rect: 'list[list[Char]]' = []
        for y in range(row, row + rows):
            chars: 'list[Char]' = []
            for x in range(column, column + columns):
                char = self.get_char(row=y, column=x)
                chars.append(char)
            rect.append(chars)
        return rect
