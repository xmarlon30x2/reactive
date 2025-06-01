from contextlib import contextmanager
from contextvars import ContextVar
from dataclasses import dataclass, field
from itertools import chain
from typing import Any, Callable, Dict, Iterable, Optional, TYPE_CHECKING, List, Set

from prompt_toolkit.application import get_app
from prompt_toolkit.key_binding.key_bindings import merge_key_bindings, KeyBindingsBase

from .effects import Effects

from .state import State
from .props import Props
from .component import Component

if TYPE_CHECKING:
    from asyncio import Task
    from prompt_toolkit.layout.containers import AnyContainer
    from ..types import Args, Kwargs

@dataclass
class Tree:
    _parent: ContextVar[Optional['Component']] = field(default_factory=lambda: ContextVar('_parent', default=None), init=False)
    _component_by_id: Dict[str, 'Component'] = field(default_factory=dict[str, Any], init=False)
    _bases_by_index: List['Component'] = field(default_factory=list['Any'], init=False)
    _bases_by_keys: Dict[str, 'Component'] = field(default_factory=dict[str,'Any'], init=False)
    _active_indexs: int = field(default=0, init=False)
    _active_keys: Set[str] = field(default_factory=set[str], init=False)
    _target_focus: Optional['AnyContainer'] = field(default=None, init=False)
    _key_bindings: Optional['KeyBindingsBase'] = field(default=None, init=False)
    _focus_task: 'Optional[Task[None]]' = field(default=None, init=False)

    def reference(self, component: 'Component'):
        new_id = component.props.id
        if new_id in self._component_by_id:
            raise ValueError(f'Se ha referenciado un componente con una ID ya existente: {new_id}')
        if new_id:
            self._component_by_id[new_id] = component

        if not component.relations.parent:
            key = component.props.key
            if key and key in self._bases_by_keys:
                raise ValueError(f'Se esta referenciando un componente base con una key ya creada: {key}')
            elif key:
                self._bases_by_keys[key] = component
            elif component in self._bases_by_index:
                raise ValueError(f'Se esta referenciado un componente base ya creado: {component}')
            else:
                self._bases_by_index.append(component)

    def unreference(self, component: 'Component') -> None:
        id = component.props.id
        if id:
            self._component_by_id.pop(id, None)
        key = component.props.key
        if key:
            self._bases_by_keys.pop(key, None)
            if key in self._active_keys:
                self._active_keys.remove(key)

        base_index = self._bases_by_index.index(component)
        if base_index != -1:
            self._bases_by_index.pop(base_index)
            
            if self._active_indexs > base_index:
                self._active_indexs -= 1

    def component_by_id(self, id: str) -> Optional['Component']:
        return self._component_by_id.get(id)

    @contextmanager
    def current_component(self, component: 'Component'):
        token = self._parent.set(component)
        try:
            yield

        finally:
            self._parent.reset(token)

    def get_current_component(self) -> 'Component':
        parent = self._parent.get()
        
        if not parent:
            raise RuntimeError('No se ha establecido componente actual')
        
        return parent

    def active_component(self,
                         func: Callable[...,Any],
                         args: 'Args',
                         kwargs: 'Kwargs'
                        ) -> 'Component':
        parent = self._parent.get()
        props = Props(args=args, kwargs=kwargs)
        key = props.key

        if parent:
            if children:=parent.relations.get_unactive_child(key=key):
                parent.relations.active_child(children)
                return children

            state = State()
            effects = Effects()
            new_children = Component(func, props=props, state=state, effects=effects)
            new_children.relations.set_parent(new_parent=parent)
            new_children.mount(self)
            parent.relations.active_child(new_children)
            return new_children

        if key and key in self._bases_by_keys:
            base = self._bases_by_keys[key]
            self.active_base(base)
            return base

        if self._active_indexs < len(self._bases_by_index):
            base = self._bases_by_index[self._active_indexs]
            self.active_base(base)
            return base
        
        state = State()
        effects = Effects()
        new_base = Component(func, props=props, state=state, effects=effects)
        new_base.mount(self)
        self.active_base(new_base)
        return new_base

    def active_base(self, base: 'Component'):
        key = base.props.key
        if key:
            if key not in self._bases_by_keys:
                raise ValueError(f'No se puede activar un componente base con una key no incluida en el arbol: {key}')
            self._active_keys.add(key)
            return

        index = self._bases_by_index.index(base)
        if index == -1:
            raise ValueError('No se puede activar un componente base no incluido en le arbol')
        
        if index != self._active_indexs:
            raise ValueError('Se esta usando un componente base fuera de orden')
        
        self._active_indexs += 1
    
    def transition(self, before: 'AnyContainer', after: 'AnyContainer'):
        if not self._target_focus and get_app().layout.has_focus(before):
            self._target_focus = after

    def flip(self):
        unused_keys = set(self._bases_by_keys.keys()) - self._active_keys
        for unused_key in unused_keys:
            child = self._bases_by_keys[unused_key]
            child.unmount(self)

        self._active_keys.clear()

        # Limpiar por índice (los que no fueron accedidos)
        unused_child = self._bases_by_index[self._active_indexs: ]
        for child in unused_child:
            child.unmount(self)
        self._active_indexs = 0

        self._key_bindings = self._merge_key_bildings()
        
        # if self._target_focus:
        #     get_app().layout.focus(self._target_focus)
        
        # -- Anterior implementacion --
        if self._target_focus:
            app = get_app()
            if self._focus_task:
                self._focus_task.cancel()
            
            self._focus_task = app.create_background_task(
                self._update_focus(focus=app.layout.focus, target=self._target_focus)
            )

            self._target_focus = None

    async def _update_focus(self, focus: 'Callable[[AnyContainer], None]', target: 'AnyContainer'):
        try:
            focus(target)
        except ValueError:
            pass

    @property
    def bases(self) -> Iterable['Component']:
        return chain(self._bases_by_index, self._bases_by_keys.values())

    @property
    def components(self):
        def flatter_components(childrens: Iterable['Component']) -> Iterable['Component']:
            for children in childrens:
                yield from children.relations.childrens
        return flatter_components(self.bases)

    @property
    def key_bindings(self) -> Optional['KeyBindingsBase']:
        return self._key_bindings

    def _merge_key_bildings(self) -> 'Optional[KeyBindingsBase]':
        list_key_bindings = list(set(
            component.key_bindings
            for component in self.components
            if component.has_key_bindings
        ))
        
        if list_key_bindings:
            return merge_key_bindings(list_key_bindings)
