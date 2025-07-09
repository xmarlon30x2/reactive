from dataclasses import dataclass, field
from itertools import chain
from typing import Any, Dict, Iterable, Optional, TYPE_CHECKING, Set


if TYPE_CHECKING:
    from .tree import Tree
    from .component import Component

__all__ = ['Relations']

@dataclass
class Relations:
    """
    Gestiona las relaciones jerárquicas entre componentes (padre-hijos).
    
    Atributos:
        _component: Componente dueño de estas relaciones
        _parent: Componente padre
        _childrens_by_index: Hijos sin key (ordenados por índice)
        _childrens_by_key: Hijos con key (accesibles por clave)
        _active_keys: Keys de hijos activos en el render actual
        _active_indexs: Índice actual para hijos sin key
        
    Métodos clave:
        add_child(child): Añade un hijo
        remove_child(child): Elimina un hijo
        active_child(child): Marca hijo como usado en el render actual
        get_unactive_child(key): Obtiene hijo no utilizado para reutilizar
        set_parent(new_parent): Establece nuevo padre
        cleanup(tree): Elimina hijos no utilizados
    """
    _component: 'Component'
    _parent: Optional['Component'] = field(default=None, init=False)
    _childrens_by_index: list['Component'] = field(default_factory=list[Any], init=False)
    _childrens_by_key: Dict[str, 'Component'] = field(default_factory=dict[str, Any], init=False)
    _active_keys: Set[str] = field(default_factory=set[str], init=False)
    _active_indexs: int = field(default=0, init=False)
    _dirty: Optional[bool] = None

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
            self._childrens_by_index.copy(),
            list(self._childrens_by_key.values())
        )

    def cleanup(self, tree: 'Tree') -> None:
        """
        Limpia los hijos no utilizados en el render actual.

        Args:
            tree: Árbol donde se desmontarán los componentes

        Process:
            1. Elimina hijos por key no utilizados
            2. Elimina hijos por índice no accedidos
            3. Reinicia contadores de actividad
        """
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
        """
        Elimina un componente hijo.
        
        Args:
            child: Componente hijo a eliminar
        """
        if child.props.key in self._childrens_by_key:
            self._childrens_by_key.pop(child.props.key)
        
        try:
            child_index = self._childrens_by_index.index(child)
        
        except ValueError:
            pass
        
        else:
            self._childrens_by_index.pop(child_index)
    
            if self._active_indexs > child_index:
                self._active_indexs -= 1

    def add_child(self, child: 'Component'):
        """
        Añade un componente como hijo.
        
        Args:
            child: Componente hijo a añadir
            
        Raises:
            ValueError: Si ya existe un hijo con la misma key
                    O si se intenta añadir el mismo hijo dos veces
        """
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
        """
        Marca un hijo como activo en el render actual.
        
        Args:
            child: Componente hijo a marcar como activo
            
        Raises:
            ValueError: Si el hijo no pertenece al padre
                    O si se activa fuera de orden (para hijos sin key)
        """
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
        """
        Obtiene un hijo no activado en el render actual.

        Args:
            key: Key del hijo a buscar (opcional)

        Returns:
            Componente hijo no utilizado o None

        Raises:
            RuntimeError: Si se detecta duplicación de keys

        Note:
            Para hijos sin key, sigue el orden secuencial
        """
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
        """
        Establece un nuevo componente padre.

        Args:
            new_parent: Nuevo componente padre

        Raises:
            ValueError: Si ya tiene un padre asignado

        Note:
            No maneja automáticamente las relaciones inversas
        """
        if self._parent and new_parent:
            raise ValueError(f'Ya se ha establecido un padre para este componente: {self._parent}')
        self._parent = new_parent
