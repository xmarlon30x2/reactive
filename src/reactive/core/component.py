from dataclasses import dataclass, field
from typing import Any, Callable, Iterable, Optional, TYPE_CHECKING
from prompt_toolkit.widgets.base import Label
from prompt_toolkit.layout.containers import HSplit
from prompt_toolkit.key_binding import KeyBindings


from .relations import Relations
from .effects import Effects
from .state import State
from .props import Props

if TYPE_CHECKING:
    from ..types import Args, Kwargs
    from .tree import Tree
    from ..types import Node, AnyContainer

__all__ = ['Component', 'transform_node']


def transform_node(node: 'Node') -> 'AnyContainer':
    """Convierte el nodo en contenedor real"""
    if node is None:
        return Label('')
    
    if isinstance(node, str):
        return Label(node)
    
    if isinstance(node, Iterable):
        containers = [transform_node(child) for child in node if child is not None]
        return HSplit(containers)

    return node

@dataclass
class Component:
    render: Callable[..., 'AnyContainer']
    props: 'Props'
    state: 'State'
    effects: 'Effects'
    relations: 'Relations' = field(init=False)
    _dirty: bool = field(init=False, default=False)
    _container: Optional['AnyContainer'] = field(init=False, default=None)
    _key_bindings: Optional['KeyBindings'] = field(init=False, default=None)
    
    def __hash__(self):
        _id = id(self)
        return hash(_id)

    def __post_init__(self):
        self.relations = Relations(self)

    @property
    def dirty(self):
        component_dirty = self._dirty
        props_dirty = self.props.dirty
        relations_dirty = self.relations.dirty
        return component_dirty or props_dirty or relations_dirty

    @property
    def key_bindings(self) -> 'KeyBindings':
        if not self._key_bindings:
            self._key_bindings = KeyBindings()
        return self._key_bindings

    @property
    def has_key_bindings(self) -> bool:
        return True if self._key_bindings else False

    def set_dirty(self):
        """Marca el componente como sucio"""
        self._dirty = True

    def render_component(self, tree: 'Tree', args: 'Args', kwargs: "Kwargs") -> 'AnyContainer':
        """Renderiza el componente y sus hijos"""
        self.props.update(args, kwargs)
        if self._container and not self.dirty:
            return self._container

        with tree.current_component(self):
            # Ejecutar renderizado
            args, kwargs = self.props.transform(self.render)
            node = self.render(*args, **kwargs)
            
            # Procesar el nodo
            container = transform_node(node)
            if self._container:
                tree.transition(before=self._container, after=container)
            self._container = container

            # Limpia y prepara para el siguiente render
            self.props.cleanup()
            self.state.cleanup()
            self.relations.cleanup(tree=tree)
            self._dirty = False
            self.effects.execute_end_render()

            return container

    def mount(self, tree: 'Tree'):
        tree.reference(self)
        
        parent = self.relations.parent
        if parent:
            parent.relations.add_child(self)

        for children in self.relations.childrens:
            children.mount(tree)

    def unmount(self, tree: 'Tree'):
        self.effects.execute_unmount()
        parent = self.relations.parent
        if parent:
            parent.relations.remove_child(self)
        
        for children in self.relations.childrens:
            children.unmount(tree)
        
        tree.unreference(self)

    @classmethod
    def new(cls, render: Callable[..., Any], *args: Any, **kwargs: Any) -> 'Component':
        state = State()
        props = Props(args, kwargs)
        effects = Effects()
        return cls(render=render, props=props, state=state, effects=effects)

    @property
    def name(self) -> str:
        return self.render.__name__

    def __str__(self) -> str:
        string = self.name
        if id:=self.props.id:
            string += f' {id=}'
        if key:=self.props.key:
            string += f' {key=}'
        return f'({string})'
