from dataclasses import dataclass, field
from itertools import chain
from typing import Any, Dict, Iterable, Optional, TYPE_CHECKING, Set


if TYPE_CHECKING:
    from .tree import Tree
    from .component import Component

__all__ = ['Relations']

@dataclass
class Relations:
    _component: 'Component'
    _parent: Optional['Component'] = field(default=None, init=False)
    _childrens_by_index: list['Component'] = field(default_factory=list[Any], init=False)
    _childrens_by_key: Dict[str, 'Component'] = field(default_factory=dict[str, Any], init=False)
    _active_keys: Set[str] = field(default_factory=set[str], init=False)
    _active_indexs: int = field(default=0, init=False)
    _dirty: Optional[bool] = None
    # def change_parent(self, new_parent: 'Component') -> None:
    #     if self._parent:
    #         self._parent.relations.remove_child(self._component)
    #     new_parent.relations.add_child(self._component)

    @property
    def parent(self) -> 'Optional[Component]':
        return self._parent

    @property
    def dirty(self) -> bool:    
        for children in self.childrens:
            if children.dirty:
                return True
        return False
        
    @property
    def childrens(self) -> Iterable['Component']:
        return chain(
            self._childrens_by_index,
            self._childrens_by_key.values()
        )

    def cleanup(self, tree: 'Tree') -> None:
        """Elimina los hijos no usados en el render actual"""
        # Limpiar por key
        unused_keys = set(self._childrens_by_key.keys()) - self._active_keys
        for unused_key in unused_keys:
            child = self._childrens_by_key[unused_key]
            child.unmount(tree)

        self._active_keys.clear()

        # Limpiar por índice (los que no fueron accedidos)
        unused_child = self._childrens_by_index[self._active_indexs: ]
        for child in unused_child:
            child.unmount(tree)
        self._active_indexs = 0

    def remove_child(self, child: 'Component'):
        if child.props.key in self._childrens_by_key:
            self._childrens_by_key.pop(child.props.key)
        
        child_index = self._childrens_by_index.index(child)
        self._childrens_by_index.remove(child)
        
        if self._active_indexs > child_index:
            self._active_indexs -= 1

    def add_child(self, child: 'Component'):
        key = child.props.key
        if key:
            if key in self._childrens_by_key:
                raise ValueError('No se puede tener dos hijos con la misma key')
            self._childrens_by_key[key] = child
        else:
            if child in self._childrens_by_index:
                raise ValueError('No se puede agregar el mismo hijo mas de una vez')
            self._childrens_by_index.append(child)

    def active_child(self, child: 'Component') -> None:
        key = child.props.key
        if key:
            if key not in self._childrens_by_key:
                raise ValueError('No se puede usar un hijo que no pertenece al padre')
            self._active_keys.add(key)
            return

        index = self._childrens_by_index.index(child)
        if index == -1:
            raise ValueError('No se puede usar un hijo que no pertenece al padre')
        
        if index != self._active_indexs:
            raise ValueError('Se esta usando a un hijo fuera del orden')
        
        self._active_indexs += 1

    def get_unactive_child(self, key: Optional[str] = None) -> Optional['Component']:
        if key:
            if key in self._active_keys:
                raise RuntimeError(f'Se ha detectado dos veces la misma key: {key}')

            child = self._childrens_by_key.get(key)
            return child

        if key in self._active_keys:
            raise RuntimeError(f'Se ha detectado dos veces la misma key: {key}')
        
        childrens_count = len(self._childrens_by_index)
        if not self._active_indexs < childrens_count:
            return None
        
        return self._childrens_by_index[self._active_indexs]

    def set_parent(self, new_parent: 'Component'):
        if self._parent and new_parent:
            raise ValueError(f'Ya se ha establecido un padre para este componente: {self._parent}')
        self._parent = new_parent
