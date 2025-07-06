from typing import Any, NamedTuple, Self
from prompt_toolkit.styles import Attrs
from prompt_toolkit.data_structures import Size as SizePT, Point as PointPT

__all__ = ['Char', 'Point', 'Size', 'Style']

class Style(Attrs):
    """Representa estilos de texto con constructor flexible"""
    
    @classmethod
    def new(
        cls,
        color: str | None = None,
        bgcolor: str | None = None,
        bold: bool | None = None,
        underline: bool | None = None,
        strike: bool | None = None,
        italic: bool | None = None,
        blink: bool | None = None,
        reverse: bool | None = None,
        hidden: bool | None = None
    ) -> Self:
        return cls(
            color=color,
            bgcolor=bgcolor,
            bold=bold,
            underline=underline,
            strike=strike,
            italic=italic,
            blink=blink,
            reverse=reverse,
            hidden=hidden
        )

    @classmethod
    def default(cls) -> 'Self':
        return cls(
            color=None,
            bgcolor=None,
            bold=None,
            underline=None,
            strike=None,
            italic=None,
            blink=None,
            reverse=None,
            hidden=None,
        )

    @classmethod
    def from_attrs(cls, attrs: Attrs) -> Self:
        return cls(
            color=attrs.color,
            bgcolor=attrs.bgcolor,
            bold=attrs.bold,
            underline=attrs.underline,
            strike=attrs.strike,
            italic=attrs.italic,
            blink=attrs.blink,
            reverse=attrs.reverse,
            hidden=attrs.hidden
        )

class Char(NamedTuple):
    """
    Representa un carácter con su estilo asociado.
    
    Atributos:
        data: Carácter (string de un solo caracter)
        style: Estilo aplicado al carácter
        
    Métodos:
        space: Crea un carácter espacio con estilo predeterminado
    """
    data: str
    style: Style

    @classmethod
    def space(cls) -> Self:
        return cls(
            data=' ',
            style=Style.default()
        )

class Point(NamedTuple):
    """
    Representa una posición en una cuadrícula 2D (fila, columna).
    
    Atributos:
        row: Posición vertical (fila)
        column: Posición horizontal (columna)
        
    Métodos:
        zero: Crea un punto en (0, 0)
        from_pt: Convierte PointPT de Prompt Toolkit
        Operadores: +, - para operaciones vectoriales
    """
    row: int
    column: int

    @classmethod
    def zero(cls) -> Self:
        return cls(row=0, column=0)

    @classmethod
    def from_pt(cls, point: PointPT) -> Self:
        return cls(row=point.y, column=point.x)

    def __add__(self, other: tuple[object, ...]) -> 'Point':
        if not isinstance(other, Point):
            raise ValueError('No se puede sumar')
        return Point(row=self.row + other.row, column=self.column + other.column)

    def __sub__(self, other: tuple[object, ...]) -> 'Point':
        if not isinstance(other, Point):
            raise ValueError('No se puede restar')
        return Point(row=self.row - other.row, column=self.column - other.column)

    def __str__(self) -> str:
        return f"(fila={self.row}, columna={self.column})"

class Size(SizePT):
    """
    Representa dimensiones en una cuadrícula (filas, columnas).
    
    Hereda de SizePT de Prompt Toolkit y añade operaciones adicionales.
    
    Métodos:
        one: Crea un tamaño de 1x1
        from_pt: Convierte SizePT de Prompt Toolkit
        Operadores: +, -, >, >=, <, <= para comparaciones y operaciones
    """
    @classmethod
    def one(cls) -> Self:
        return cls(rows=1, columns=1)

    @classmethod
    def from_pt(cls, point: SizePT) -> Self:
        return cls(rows=point.rows, columns=point.columns)

    def __lt__(self, other: tuple[int, ...]) -> bool:
        if not isinstance(other, Size):
            raise ValueError('No se puede comparar')
        return other.rows > self.rows and other.columns > self.columns

    def __le__(self, other: tuple[int, ...]) -> bool:
        if not isinstance(other, Size):
            raise ValueError('No se puede comparar')
        return other.rows >= self.rows and other.columns >= self.columns
    
    def __gt__(self, other: tuple[int, ...]) -> bool:
        if not isinstance(other, Size):
            raise ValueError('No se puede comparar')
        return other.rows < self.rows and other.columns < self.columns
    
    def __ge__(self, other: tuple[int, ...]) -> bool:
        if not isinstance(other, Size):
            raise ValueError('No se puede comparar')
        return other.rows <= self.rows and other.columns <= self.columns

    def __add__(self, other: tuple[object, ...]) -> 'Size':
        if not isinstance(other, Size):
            raise ValueError('No se puede sumar')
        return Size(rows=self.rows + other.rows, columns=self.columns + other.columns)

    def __sub__(self, other: tuple[object, ...]) -> 'Size':
        if not isinstance(other, Size):
            raise ValueError('No se puede restar')
        return Size(rows=self.rows - other.rows, columns=self.columns - other.columns)

class Box(NamedTuple):
    """
    Representa un área rectangular definida por posición y tamaño.
    
    Atributos:
        point: Esquina superior izquierda (Point)
        size: Dimensiones del área (Size)
        
    Métodos:
        from_position_and_size: Crea un Box desde coordenadas
        collide: Comprueba si un punto colisiona con el área
        __contains__: Comprueba si un punto u otro Box están contenidos
    """
    point: Point
    size: Size

    @classmethod
    def from_position_and_size(cls, row: int, column: int, rows: int, columns: int) -> Self:
        size = Size(rows=rows, columns=columns)
        point = Point(row=row, column=column)
        return cls(size=size, point=point)
    
    def desplace(self, rows: int, columns: int):
        point = Point(self.point.row + rows, self.point.column + columns)
        return Box(point=point, size=self.size)
    
    def collide(self, obj: Point) -> bool:
        return self.size.rows > obj.row >= 0 and self.size.columns > obj.column >= 0

    def __contains__(self, item: Any) -> bool:
        if not isinstance(item, (Box, Point)):
            raise ValueError()

        point = item.point if isinstance(item, Box) else item
        
        in_row_space = self.size.rows + self.point.row > point.row >= self.point.row
        in_column_space = self.size.columns + self.point.column > point.column >= self.point.column
        origin_inside = in_column_space and in_row_space
        
        if (not isinstance(item, Box)) or not origin_inside:
            return origin_inside

        other_in_row_space = self.size.rows + self.point.row >= (point.row + item.size.rows) > self.point.row
        other_in_column_space = self.size.columns + self.point.column >= (point.column + item.size.columns) > self.point.column
        return other_in_row_space and other_in_column_space
