from typing import Any, TYPE_CHECKING, Optional, Union

from .utils import factory_value

if TYPE_CHECKING:
    from ..types import Setter, Computer

__all__ = ['State']


class State:
    _slices: dict[int, Any]

    def __init__(self):
        self._slices = {}
        self._active_indexs = -1

    def get_slice[S](self,
                        index: int,
                        default: Optional[S] = None,
                        default_factory: 'Optional[Setter[S]]' = None
                    ) -> Any:
        if not index in self._slices:
            new_slice = default_factory() if default_factory else default
            self._slices[index] = new_slice
            return new_slice

        return self._slices[index]

    def set_slice(self,
                    index: int,
                    value: Optional[Any] = None, 
                    value_factory: 'Optional[Union[Setter[Any], Computer[Any]]]' = None
                ):
        current_slice = self._slices.get(index, None)
        self._slices[index] = value if not value_factory else factory_value(current_slice, value_factory)

    def get_index(self) -> int:
        return self._active_indexs

    def active_hook(self) -> None:
        self._active_indexs += 1

    def cleanup(self) -> None:
        for index in list(self._slices.keys()):
            if not index <= self._active_indexs:
                self._slices.pop(index)
        self._active_indexs = -1

