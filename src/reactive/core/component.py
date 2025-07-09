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
    """
    Convierte nodos de alto nivel en contenedores reales de Prompt Toolkit.
    
    Args:
        node: Elemento a transformar. Puede ser:
            - None: Se convierte en Label vacío
            - str: Se convierte en Label
            - Iterable: Se convierte en HSplit de nodos hijos
            - Cualquier otro tipo: Se asume que ya es un contenedor válido
    
    Returns:
        Contenedor de Prompt Toolkit listo para renderizar
        
    Ejemplo:
        >>> transform_node("Hola Mundo")
        Label(text='Hola Mundo')
    """
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
    """
    Representa un componente en el framework Reactive.
    
    Atributos:
        render (Callable): Función que define la UI del componente
        props (Props): Propiedades del componente
        state (State): Estado interno del componente
        effects (Effects): Gestor de efectos secundarios
        relations (Relations): Relaciones padre-hijo con otros componentes
        _dirty (bool): Indica si el componente necesita re-render
        _container (AnyContainer): Contenedor renderizado actualmente
        _key_bindings (KeyBindings): Bindings de teclado asociados
        
    Métodos clave:
        render_component: Genera la representación UI actual
        mount: Registra el componente en el árbol de UI
        unmount: Elimina el componente del árbol de UI
        set_dirty: Marca el componente para re-render
    """
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
        """
        Renderiza el componente y sus hijos.
        
        Args:
            tree: Árbol de componentes actual
            args: Argumentos posicionales para el render
            kwargs: Argumentos clave para el render
            
        Returns:
            Contenedor de Prompt Toolkit actualizado
            
        Proceso:
            1. Actualiza propiedades si cambiaron
            2. Ejecuta la función render si el componente está "dirty"
            3. Transforma el nodo resultante en contenedor real
            4. Gestiona transiciones de UI
            5. Limpia estados temporales
            6. Ejecuta efectos post-render
        """
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

    def mount(self, tree: 'Tree') -> None:
        """
        Monta el componente en el árbol de UI.
        
        Args:
            tree: Árbol donde se montará el componente
            
        Proceso:
            1. Registra el componente en el árbol
            2. Establece relación con el componente padre
            3. Monta recursivamente a los hijos
        """
        tree.reference(self)
        
        parent = self.relations.parent
        if parent:
            parent.relations.add_child(self)

        for children in self.relations.childrens:
            children.mount(tree)

    def unmount(self, tree: 'Tree'):
        """
        Desmonta el componente del árbol de UI.
        
        Args:
            tree: Árbol del que se desmontará
            
        Proceso:
            1. Ejecuta efectos de desmontaje
            2. Rompe relación con el componente padre
            3. Desmonta recursivamente a los hijos
            4. Elimina referencia del árbol
        """
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
