from dataclasses import dataclass
from itertools import chain
from typing import Generator, Optional, Pattern, Self, overload, TYPE_CHECKING
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
        return self._get_text()

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
        desplace_box = box.desplace(rows=self.point.row, columns=self.point.column)
        return ExpectText.from_box(expect=self._expect, box=desplace_box)

    def contains(self, *texts: str) -> Self:
        """Asegura que el texto contiene todos los textos especificados"""
        missing = [text for text in texts if text not in self.text]
        if missing:
            missing_str = ', '.join(f'"{t}"' for t in missing)
            raise AssertionError(f'Expected text to contain {missing_str}, but got "{self.text}"')
        return self

    def not_contains(self, *texts: str) -> Self:
        """Asegura que el texto no contiene ninguno de los textos especificados"""
        found = [text for text in texts if text in self.text]
        if found:
            found_str = ', '.join(f'"{t}"' for t in found)
            raise AssertionError(f'Expected text to not contain {found_str}, but got "{self.text}"')
        return self

    def startswith(self, text: str) -> Self:
        """Asegura que el texto comience con el texto especificado"""
        assert self.text.startswith(text), f'Expected text to start with "{text}", but got "{self.text}"'
        return self

    def endswith(self, text: str) -> Self:
        """Asegura que el texto termine con el texto especificado"""
        assert self.text.endswith(text), f'Expected text to end with "{text}", but got "{self.text}"'
        return self

    def count(self, text: str, n: int) -> Self:
        occurrences = self.text.count(text)
        assert occurrences == n, f'Expected {n} occurrences of "{text}", but found {occurrences} in "{self.text}"'
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
            return self._create_subarea(box)
        elif row is not None and column is not None:
            return self._create_subarea_from_coords(row, column, rows, columns)
        raise ValueError("Invalid arguments for subarea")

    def _create_subarea(self, box: Box) -> 'ExpectText':
        """Crea una subárea a partir de un Box relativo"""
        absolute_point = self.point + box.point
        absolute_box = Box(point=absolute_point, size=box.size)
        assert absolute_box in self.box
        return ExpectText.from_box(expect=self._expect, box=absolute_box)

    def _create_subarea_from_coords(
        self,
        row: int,
        column: int,
        rows: int | None,
        columns: int | None
    ) -> 'ExpectText':
        """Crea una subárea a partir de coordenadas relativas"""
        rows = rows or self.size.rows - row
        columns = columns or self.size.columns - column
        absolute_point = Point(
            row=self.point.row + row,
            column=self.point.column + column
        )
        new_box = Box(
            point=absolute_point,
            size=Size(rows=rows, columns=columns)
        )
        assert new_box in self.box
        return ExpectText.from_box(expect=self._expect, box=new_box)
    
    @overload
    def at(self, *, row: int) -> Self: ...
    
    @overload
    def at(self, *, column: int) -> Self: ...
    
    @overload
    def at(self, *, point: Point) -> Self: ...
    
    @overload
    def at(self, *, row: int, column: int) -> Self: ...

    def at(self,
            *,
            row: Optional[int] = None,
            column: Optional[int] = None,
            point: Optional[Point] = None
        ) -> Self:
        """Valida la posición del cursor"""
        target = self._get_target_point(row, column, point)
        self._assert_position(target)
        return self

    def _get_target_point(
        self,
        row: Optional[int],
        column: Optional[int],
        point: Optional[Point]
    ) -> Point:
        """Determina el punto objetivo basado en los parámetros"""
        if point is not None:
            return point
        if row is not None and column is not None:
            return Point(row=row, column=column)
        if row is not None:
            return Point(row=row, column=self.point.column)
        if column is not None:
            return Point(column=column, row=self.point.row)
        raise ValueError("Debe especificar al menos un parámetro (fila, columna o punto)")

    def _assert_position(self, target: Point) -> None:
        """Verifica que la posición actual coincida con la objetivo"""
        if target == self.point:
            return

        # Generar representación visual para mensaje de error
        screen_lines = self._expect.screen.split('\n')
        annotated_screen: list[str] = []
        
        # Anotar cada línea con marcadores de posición
        for i, line in enumerate(screen_lines):
            prefix = ""
            if i == target.row and i == self.point.row:
                prefix = "E/A |"
            elif i == target.row:
                prefix = "E   |"
            elif i == self.point.row:
                prefix = "A   |"
            else:
                prefix = "    |"
            annotated_screen.append(f"{prefix}{line}|")
        
        # Añadir marcadores de columna
        marker_lines: list[str] = []
        if target.row == self.point.row:
            # Ambos en misma fila
            marker_line = [' '] * (self._expect.size.columns + 6)
            if target.column < len(marker_line):
                marker_line[5 + target.column] = 'E'
            if self.point.column < len(marker_line):
                marker_line[5 + self.point.column] = 'A'
            marker_lines.append("     " + ''.join(marker_line))
        else:
            # Marcadores separados para diferentes filas
            if target.row < len(screen_lines):
                marker_line = [' '] * (self._expect.size.columns + 6)
                if target.column < len(marker_line):
                    marker_line[5 + target.column] = 'E'
                marker_lines.append("     " + ''.join(marker_line))
            
            if self.point.row < len(screen_lines):
                marker_line = [' '] * (self._expect.size.columns + 6)
                if self.point.column < len(marker_line):
                    marker_line[5 + self.point.column] = 'A'
                marker_lines.append("     " + ''.join(marker_line))
        
        # Construir mensaje de error completo
        screen_visual = "\n".join(chain(
            annotated_screen,
            marker_lines,
            [f"     {'-' * self._expect.size.columns}"]
        ))
        
        # Lanzar error con información detallada
        raise AssertionError(
            f"Posición esperada: {target}\n"
            f"Posición actual: {self.point}\n"
            f"Visualización:\n{screen_visual}\n"
            "Leyenda: E=Posición esperada, A=Posición actual"
        )

    def row(self, row: int) -> 'ExpectText':
        """Devuelve una fila específica"""
        self._validate_row(row)
        absolute_point = Point(
            row=self.point.row + row,
            column=self.point.column
        )
        new_box = Box(
            point=absolute_point,
            size=Size(rows=1, columns=self.size.columns)
        )
        return ExpectText.from_box(expect=self._expect, box=new_box)

    def _validate_row(self, row: int) -> None:
        """Valida que la fila esté dentro del rango"""
        assert 0 <= row < self.size.rows, (
            f"Row {row} out of bounds [0, {self.size.rows})"
        )

    def below(self, rows: int | None = None) -> 'ExpectText':
        """Devuelve el área inferior"""
        rows = rows or self._expect.size.rows - (self.point.row + self.size.rows)
        self._validate_positive(rows, "rows")
        return self._create_adjacent_area(
            row_offset=self.size.rows,
            rows=rows
        )

    def above(self, rows: int | None = None) -> 'ExpectText':
        """Devuelve el área superior"""
        rows = rows or self.point.row
        self._validate_positive(rows, "rows")
        return self._create_adjacent_area(
            row_offset=-rows,
            rows=rows
        )

    def back(self, columns: int | None = None) -> 'ExpectText':
        """Devuelve el área a la izquierda"""
        columns = columns or self.point.column
        self._validate_positive(columns, "columns")
        return self._create_adjacent_area(
            column_offset=-columns,
            columns=columns
        )

    def forward(self, columns: int | None = None) -> 'ExpectText':
        """Devuelve el área a la derecha"""
        columns = columns or self._expect.size.columns - (self.point.column + self.size.columns)
        self._validate_positive(columns, "columns")
        return self._create_adjacent_area(
            column_offset=self.size.columns,
            columns=columns
        )

    def _validate_positive(self, value: int, name: str) -> None:
        """Valida que el valor sea positivo"""
        assert value > 0, f"{name} must be positive, got {value}"

    def _create_adjacent_area(
        self,
        row_offset: int = 0,
        column_offset: int = 0,
        rows: int | None = None,
        columns: int | None = None
    ) -> 'ExpectText':
        """Crea un área adyacente con desplazamiento"""
        new_row = self.point.row + row_offset
        new_column = self.point.column + column_offset
        
        return ExpectText.from_position_and_size(
            expect=self._expect,
            row=new_row,
            column=new_column,
            rows=rows or self.size.rows,
            columns=columns or self.size.columns
        )

    def _get_text(self) -> str:
        rect = self._expect.terminal.get_rect(box=self.box)
        return get_text_from_rect(rect)

    def _iter_chars(self) -> Generator[tuple['Point', 'Char']]:
        rect = self._expect.terminal.get_rect(box=self.box)
        for row, columns in enumerate(rect):
            for column, char in enumerate(columns):
                yield Point(row=row, column=column), char
