from dataclasses import dataclass, field
from inspect import signature
from typing import Any, Callable, Optional, Tuple, TYPE_CHECKING

if TYPE_CHECKING:
    from ..types import Args, Kwargs

__all__ = ['Props', 'MAGIC_PROPS']


MAGIC_PROPS = ('id', 'key')

@dataclass
class Props:
    args: 'Args'
    kwargs: 'Kwargs'
    _dirty: bool = field(default=False, init=False)

    def transform(self, func: Callable[..., Any]) -> Tuple['Args', 'Kwargs']:
        parameters = signature(func).parameters
        kwargs = {key:value for (key,value) in self.kwargs.items() if key not in MAGIC_PROPS}
        if 'id' in parameters:
            kwargs['id'] = self.id
        if 'key' in parameters:
            kwargs['key'] = self.key
        return self.args, kwargs

    def update(self, args: 'Args', kwargs: 'Kwargs'):
        if args != self.args:
            self.args = args
            self._dirty = True

        if kwargs != self.kwargs:
            self.kwargs = kwargs
            self._dirty = True

        return self._dirty

    @property
    def dirty(self) -> bool:
        return self._dirty

    @property
    def key(self) -> Optional[str]:
        return self.kwargs.get('key')

    @property
    def id(self) -> Optional[str]:
        return self.kwargs.get('id')

    def cleanup(self):
        self._dirty = False
