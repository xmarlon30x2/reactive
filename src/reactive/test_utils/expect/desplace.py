from abc import abstractmethod
from typing import TYPE_CHECKING

from ...data_structures import Box

if TYPE_CHECKING:
    from .point import ExpectPoint
    from .expect import Expect

__all__ = ['DesplaceBase']

class DesplaceBase:
    _expect: 'Expect'

    @property
    @abstractmethod
    def box(self) -> 'Box': ...

    def down(self, steps: int = 1) -> 'ExpectPoint':
        """Devuelve un punto hacia abajo"""
        from .point import ExpectPoint
        assert steps > 0
        row = self.box.point.row + (self.box.size.rows * steps)
        assert 0 <= row < self._expect.size.rows
        return ExpectPoint.from_position(
            expect=self._expect,
            row=row,
            column=self.box.point.column
        )

    def up(self, steps: int = 1) -> 'ExpectPoint':
        """Devuelve un punto hacia arriba"""
        from .point import ExpectPoint
        assert steps > 0
        row = self.box.point.row - (self.box.size.rows * steps)
        assert 0 <= row < self._expect.size.rows
        return ExpectPoint.from_position(
            expect=self._expect,
            row=row,
            column=self.box.point.column
        )

    def left(self, steps: int = 1) -> 'ExpectPoint':
        """Devuelve un punto a la isquierda"""
        from .point import ExpectPoint
        assert steps > 0
        column = self.box.point.column - (self.box.size.columns * steps)
        assert 0 <= column < self._expect.size.columns
        return ExpectPoint.from_position(
            expect=self._expect,
            column=column,
            row=self.box.point.row
        )

    def right(self, steps: int = 1) -> 'ExpectPoint':
        """Devuelve un punto a la derecha"""
        from .point import ExpectPoint
        assert steps > 0
        column = self.box.point.column + (self.box.size.columns * steps)
        assert 0 <= column < self._expect.size.columns
        return ExpectPoint.from_position(
            expect=self._expect,
            column=column,
            row=self.box.point.row
        )
