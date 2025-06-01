from typing import Any, Callable, Optional, Tuple, Union, TYPE_CHECKING
from .hook import hook
from ..core.current import get_tree

if TYPE_CHECKING:
    type _Deps = Union[None, Tuple[Any, ...]]
    type _Cleanup = Optional[Callable[[], Any]]
    type _StateType = tuple[_Cleanup, _Deps]
    type _Effect = Callable[[], Optional[_Cleanup]]

@hook
def use_effect( 
            *dependencies: Any) -> Callable[['_Effect'], None]:
    """
    Hook para efectos secundarios y manejo del ciclo de vida
    
    Args:
        dependencies: Un serie de dependencias que activan el efecto
    
    Returns:
        decorator: Decorador que acepta un función que realiza el efecto (puede retornar función de limpieza)

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
            state: '_StateType' = component.state.get_slice(hook_index)
            cleanup, _ = state
            if cleanup:
                cleanup()

        component.effects.on_unmount(execute_cleanup_on_unmout)

    def decorator(effect: '_Effect') -> None:
        def handler_effect():
            state: '_StateType' = component.state.get_slice(hook_index)
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
