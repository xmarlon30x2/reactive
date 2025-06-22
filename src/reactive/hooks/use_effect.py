from typing import Any, Callable, Optional, Tuple, Union, TYPE_CHECKING
from .hook import hook
from ..core.current import get_tree

if TYPE_CHECKING:
    type _Deps = Union[None, Tuple[Any, ...]]
    type _Cleanup = Optional[Callable[[], Any]]
    type _StateType = tuple[_Cleanup, _Deps]
    type _Effect = Callable[[], Optional[_Cleanup]]

__all__ = ['use_effect']

@hook
def use_effect( 
            *dependencies: Any) -> Callable[['_Effect'], None]:
    """
    Gestiona efectos secundarios y ciclo de vida del componente.
    
    Args:
        *dependencies: Dependencias que activan la ejecución del efecto
        
    Returns:
        Decorador que recibe la función de efecto
        
    Ejemplo:
        @use_effect(user_id)
        def fetch_data():
            # Lógica para obtener datos
            return cleanup_function  # Opcional
    
    Comportamiento:
        - Se ejecuta después del primer render (montaje)
        - Se vuelve a ejecutar cuando cambian las dependencias
        - Ejecuta la función de limpieza antes de re-ejecutar o al desmontar
    """
    tree = get_tree()
    component = tree.get_current_component()
    hook_index = component.state.get_index()
    state: _StateType = component.state.get_slice(
        hook_index,
        (None, None)
    )
    _, before_deps = state
    
    if before_deps == None:
        def execute_cleanup_on_unmout():
            state = component.state.get_slice(hook_index)
            cleanup, _ = state
            if cleanup:
                cleanup()

        component.effects.on_unmount(execute_cleanup_on_unmout)

    def decorator(effect: '_Effect') -> None:
        def handler_effect():
            state = component.state.get_slice(hook_index)
            cleanup, _ = state
            if cleanup:
                cleanup()

            new_cleanup = effect()
            component.state.set_slice(
                hook_index,
                value=(new_cleanup, dependencies),
            )

        if before_deps != dependencies:
            component.effects.on_end_render(handler_effect)

    return decorator
