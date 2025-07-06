from typing import Generator

from ...data_structures import Char
from ...data_structures import Box, Point
from ...data_structures import Point, Size

__all__ = ['select_text', 'find_box']

def select_text(text: str | list[str], point: Point, size: Size) -> str:
    text_lines = text if isinstance(text, list) else text.split('\n')
    text_size = get_size_text(text_lines)
    assert text_size >= size
    assert (point.row + size.rows) <= text_size.rows
    assert (point.column + size.columns) <= text_size.columns

    return '\n'.join(
        map(
            lambda subrow: subrow[point.column: point.column + size.columns],
            text_lines[point.row: point.row + size.rows]
        )
    )

def indexs_of(text: str, substring: str) -> Generator[int]:
    start = 0
    while True:
        index = text.find(substring, start)

        if index == -1:
            return

        yield index

        start = index + 1

def find_box(text: str | list[str], query: str | list[str]) -> 'Box | None':
    query_lines = query if isinstance(query, list) else query.split('\n')
    query_size = get_size_text(query_lines)
    text_lines = text if isinstance(text, list) else text.split('\n')
    text_size = get_size_text(text_lines)

    assert query_size <= text_size, 'EL texto esperado es mas grande que el texto actual'

    for row, text_line in enumerate(text_lines):
        for column in indexs_of(text=text_line, substring=query_lines[0]):
            point = Point(row=row, column=column)
            text_area = select_text(text=text_lines, point=point, size=query_size)
            query_area = select_text(text=text_lines, point=point, size=query_size)

            if query_area == text_area:
                return Box(point=point, size=query_size)

    return None

def get_text_from_rect(rect: list[list['Char']]) -> str:
    lines: list[str] = []
    for row in rect:
        line = ''.join([char.data for char in row])
        lines.append(line)
    return '\n'.join(lines)

def get_size_text(text: str | list[str]) -> 'Size':
    lines = text.split('\n') if isinstance(text, str) else text
    assert len(lines) != 0
    lenghts = [len(line) for line in lines]
    columns = lenghts[0]
    assert columns != 0
    assert lenghts.count(columns) == len(lenghts), 'Todas las lineas deben tener la misma logitud'
    return Size(rows=len(lines), columns=columns)

