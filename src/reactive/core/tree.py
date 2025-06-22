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
    """
    Representa el árbol jerárquico de componentes de la aplicación.
    
    Responsabilidades:
        - Mantener referencia a todos los componentes
        - Gestionar el componente actual durante el render
        - Coordinar el montaje/desmontaje de componentes
        - Combinar key bindings de todos los componentes
        - Gestionar el foco entre renders
        
    Atributos clave:
        _component_by_id: Componentes registrados por ID
        _bases_by_index: Componentes raíz sin key
        _bases_by_keys: Componentes raíz con key
        _parent: ContextVar del componente actual
        
    Métodos principales:
        reference(comp): Registra un componente
        unreference(comp): Elimina un componente
        current_component(comp): Context manager para comp. actual
        active_component(func): Activa o crea un componente
        flip(): Finaliza el ciclo de render (limpieza + foco)
        transition(): Maneja transiciones de contenedores
    """
    _parent: ContextVar[Optional['Component']] = field(default_factory=lambda: ContextVar('_parent', default=None), init=False)
    _component_by_id: Dict[str, 'Component'] = field(default_factory=dict[str, Any], init=False)
    _bases_by_index: List['Component'] = field(default_factory=list['Any'], init=False)
    _bases_by_keys: Dict[str, 'Component'] = field(default_factory=dict[str,'Any'], init=False)
    _active_indexs: int = field(default=0, init=False)
    _active_keys: Set[str] = field(default_factory=set[str], init=False)
    _target_focus: Optional['AnyContainer'] = field(default=None, init=False)
    _key_bindings: Optional['KeyBindingsBase'] = field(default=None, init=False)
    _focus_task: 'Optional[Task[None]]' = field(default=None, init=False)

    @property
    def bases(self) -> Iterable['Component']:
        return chain(self._bases_by_index.copy(), list(self._bases_by_keys.values()))

    @property
    def components(self):
        def flatter_components(components: Iterable['Component']) -> Iterable['Component']:
            for component in components:
                yield component
                yield from flatter_components(component.relations.childrens)
        return flatter_components(self.bases)

    @property
    def key_bindings(self) -> Optional['KeyBindingsBase']:
        return self._key_bindings

    def reference(self, component: 'Component'):
        """
        Registra un componente en el árbol.
        
        Args:
            component: Componente a registrar
            
        Raises:
            ValueError: Si ya existe un componente con la misma ID o key
        """
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
        """
        Elimina todas las referencias a un componente del árbol.
        
        Proceso completo:
        1. Elimina el componente del registro por ID
        2. Elimina el componente de los registros por key (si tiene key)
        3. Elimina el componente de la lista de bases por índice (si es raíz)
        4. Ajusta los contadores de componentes activos si es necesario
        
        Args:
            component: Componente a desreferenciar
            
        Ejemplo:
            tree.unreference(my_component)
            
        Notas:
            - No desmonta el componente automáticamente (debe hacerse antes)
            - Ajusta automáticamente los índices activos si se elimina un componente base
            - Es seguro llamar múltiples veces (no lanza error si el componente ya no existe)
        """
        id = component.props.id
        if id:
            self._component_by_id.pop(id, None)
        key = component.props.key
        if key:
            self._bases_by_keys.pop(key, None)
            if key in self._active_keys:
                self._active_keys.remove(key)
        try:
            base_index = self._bases_by_index.index(component)
        except ValueError:
            pass
        else:
            self._bases_by_index.pop(base_index)
            
            if self._active_indexs > base_index:
                self._active_indexs -= 1

    def component_by_id(self, id: str) -> Optional['Component']:
        """
        Busca un componente por su ID en el árbol.

        Args:
            id: Identificador único del componente a buscar

        Returns:
            El componente encontrado o None si no existe

        Example:
            found = tree.component_by_id("user-panel")
        """
        return self._component_by_id.get(id)

    @contextmanager
    def current_component(self, component: 'Component'):
        """
        Context manager para operar en el contexto de un componente.
        
        Args:
            component: Componente a establecer como actual
            
        Yields:
            None
            
        Example:
            with tree.current_component(my_component):
                # Operaciones en contexto de my_component
        """
        token = self._parent.set(component)
        try:
            yield

        finally:
            self._parent.reset(token)

    def get_current_component_or_none(self) -> 'Optional[Component]':
        """
        Obtiene el componente actualmente en contexto sin lanzar excepciones.

        Returns:
            Componente actual o None si no hay ninguno establecido

        Note:
            Versión segura de get_current_component()
        """
        return self._parent.get()

    def get_current_component(self) -> 'Component':
        """
        Obtiene el componente actualmente en contexto obligatoriamente.

        Returns:
            Componente actual

        Raises:
            RuntimeError: Si no hay ningún componente en contexto

        Example:
            current = tree.get_current_component()
        """
        parent = self._parent.get()
        
        if not parent:
            raise RuntimeError('No se ha establecido componente actual')
        
        return parent

    def active_component(self,
                         func: Callable[...,Any],
                         args: 'Args',
                         kwargs: 'Kwargs'
                        ) -> 'Component':
        """
        Activa o crea un componente en el árbol actual.

        Args:
            func: Función render del componente
            args: Argumentos posicionales para el render
            kwargs: Argumentos clave para el render

        Returns:
            Componente activado/creado

        Process:
            1. Busca componente hijo no utilizado para reutilizar
            2. Si no existe, crea uno nuevo
            3. Establece relaciones padre-hijo
            4. Registra el componente en el árbol
        """
        parent = self._parent.get()
        props = Props(args=args, kwargs=kwargs)
        key = props.key

        if parent:
            if children:=parent.relations.get_unactive_child(key=key):
                parent.relations.active_child(children)
                return children

            state = State()
            effects = Effects()
            new_children = Component(render=func, props=props, state=state, effects=effects)
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
        new_base = Component(render=func, props=props, state=state, effects=effects)
        new_base.mount(self)
        self.active_base(new_base)
        return new_base

    def active_base(self, base: 'Component'):
        """
        Activa un componente base en el árbol.

        Args:
            base: Componente base a activar

        Raises:
            ValueError: Si el componente no está registrado como base
                    o se activa fuera de orden
        """
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
        """
        Maneja la transición de foco entre contenedores.

        Args:
            before: Contenedor actual
            after: Nuevo contenedor

        Note:
            Si el foco estaba en 'before', lo moverá a 'after'
            La transición real ocurre durante flip()
        """
        if not self._target_focus and get_app().layout.has_focus(before):
            self._target_focus = after

    def flip(self):
        """
        Finaliza el ciclo de render actual.
        
        Process:
            1. Limpia componentes base no utilizados
            2. Actualiza los key bindings combinados
            3. Maneja la transición de foco si es necesario
        """
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

    def _merge_key_bildings(self) -> 'Optional[KeyBindingsBase]':
        list_key_bindings = list(set(
            component.key_bindings
            for component in self.components
            if component.has_key_bindings
        ))
        
        if not list_key_bindings:
            return None
        
        return merge_key_bindings(list_key_bindings)
