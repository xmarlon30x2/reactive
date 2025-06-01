from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Any, Callable

if TYPE_CHECKING:
    type _Effect = Callable[[], None]

__all__ = ['Effects']

@dataclass
class Effects:
    _end_render: list['_Effect'] = field(default_factory=list[Any], init=False)
    _unmount: list['_Effect'] = field(default_factory=list[Any], init=False)

    def on_end_render(self, effect: '_Effect'):
        self._end_render.append(effect)
    
    def on_unmount(self, effect: '_Effect'):
        self._unmount.append(effect)

    def execute_end_render(self) -> None:
        while self._end_render:
            effect = self._end_render.pop(0)
            effect()
    
    def execute_unmount(self) -> None:
        while self._unmount:
            effect = self._unmount.pop(0)
            effect()
