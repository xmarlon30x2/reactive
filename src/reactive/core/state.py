from typing import Any, TYPE_CHECKING, Optional, Union

from .utils import factory_value

if TYPE_CHECKING:
    from ..types import Setter, Computer

__all__ = ['State']


class State:
    def __init__(self, slices: Optional[list[Any]] = None, index: Optional[int] = None):
        self._index = index or 0
        self._slices = slices or []

        self._validate_index(index=self._index)

    def get_slice[S](self,
                        index: int,
                        default: Optional[S] = None,
                        default_factory: 'Optional[Setter[S]]' = None
                    ) -> Any:
        lenght_slices = self._validate_index(index=index)

        if not index < lenght_slices:
            new_slice = default_factory() if default_factory else default
            self._slices.append(new_slice)

        return self._slices[index]

    def set_slice(self,
                    index: int,
                    value: Optional[Any] = None, 
                    value_factory: 'Optional[Union[Setter[Any], Computer[Any]]]' = None
                ):
        self._validate_index(index=index)
        current_slice = self._slices[index]
        self._slices[index] = value if not value_factory else factory_value(current_slice, value_factory)

    def get_index(self) -> int:
        return self._index

    def increment_index(self) -> None:
        self._index += 1

    def cleanup(self) -> None:
        if self._index:
            self._slices = self._slices[:self._index]
            self._index = 0

    def _validate_index(self, index: int) -> int:
        lenght_slices = len(self._slices)
        if index < 0 or index > lenght_slices + 1:
            raise IndexError(f'Indice fuera de rango: {index}')
        return lenght_slices

