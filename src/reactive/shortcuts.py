from asyncio import run
from typing import Callable, List, Literal, Optional, Tuple, Union
from prompt_toolkit.application.application import Application
from prompt_toolkit.layout.layout import Layout
from prompt_toolkit.layout.containers import DynamicContainer, AnyContainer, HSplit
from prompt_toolkit.key_binding.key_bindings import DynamicKeyBindings, KeyBindingsBase, merge_key_bindings

from .constants import DEFAULT_REFRESH_INTERVAL
from .key_bildings.focus import load_recovery_focus
from .components.default_fallback import DefaultFallback
from .components.error_boundary import ErrorBoundary
from .core.tree import Tree
from .core.current import open_tree

__all__ = ['run_app', 'create_root']

def create_root(
        component_func: Callable[[], 'AnyContainer'],
        fallback: Union[Optional[Callable[[str, Exception], 'AnyContainer']], Literal[False]] = False,
        recover_focus_key: Union[Optional[str], Literal[False]] = None,
        tree_instance: Optional['Tree'] = None
    ) -> Tuple['AnyContainer', 'KeyBindingsBase']:
    """
    Crea el contenedor raíz y key bindings para una aplicación CLI.
    
    Args:
        component_func: Función que renderiza el componente raíz
        fallback: Manejo de errores (False para deshabilitar, None para DefaultFallback)
        recover_focus_key: Tecla para recuperar el foco (False para deshabilitar)
        tree_instance: Árbol de componentes existente (opcional)
        
    Returns:
        Tupla (contenedor raíz, key bindings asociados)
        
    Proceso:
        1. Configura ErrorBoundary si fallback no es False
        2. Crea contenedor dinámico que actualiza el árbol
        3. Combina key bindings del árbol con el de recuperación de foco
    """
    tree = tree_instance if tree_instance is not None else Tree()

    if fallback != False:
        root_func = lambda: ErrorBoundary(
            fallback=fallback or (lambda key, exc: DefaultFallback(None, key, exception=exc)),
            children=component_func
        )
    else:
        root_func = component_func
    
    # Contenedor dinámico
    def get_container():
        nonlocal tree
        with open_tree(tree):
            container = root_func()
            tree.flip()

        return container
    root = DynamicContainer(get_container)

    root_kb: KeyBindingsBase = DynamicKeyBindings(lambda: tree.key_bindings)
    if recover_focus_key != False:
        recovery_focus = load_recovery_focus(root_target=root, key=recover_focus_key)
        root_kb = merge_key_bindings([root_kb, recovery_focus])

    return root, root_kb

def run_app(*root_containers: 'AnyContainer', 
           key_bindings: Optional['KeyBindingsBase' | List['KeyBindingsBase']] = None, 
           full_screen: bool = True, 
           refresh_interval: Optional[float] = None,
           mouse_support: bool = True
        ) -> None:
    """
    Ejecuta una aplicación CLI con los componentes especificados.
    
    Args:
        *root_containers: Contenedores raíz de la aplicación
        key_bindings: Key bindings a usar (puede ser lista para combinar)
        full_screen: Modo pantalla completa (True por defecto)
        refresh_interval: Intervalo de refresco en segundos
        mouse_support: Habilita soporte para ratón (True por defecto)
        
    Proceso:
        1. Crea un layout con los contenedores raíz
        2. Combina key bindings si es necesario
        3. Inicia la aplicación con las configuraciones especificadas
    """
    # Combinar contenedores en un layout
    layout = Layout(HSplit(root_containers))
    key_bindings = merge_key_bindings(key_bindings) if isinstance(key_bindings, list) else key_bindings
    
    app = Application[None](
        layout=layout,
        full_screen=full_screen,
        key_bindings=key_bindings,
        refresh_interval=refresh_interval or DEFAULT_REFRESH_INTERVAL,
        mouse_support=mouse_support
    )
    run(app.run_async())
