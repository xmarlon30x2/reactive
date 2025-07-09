from typing import Any, Callable, Optional, TYPE_CHECKING, Union
from prompt_toolkit.filters import Condition

from .hook import hook
from ..core.current import get_tree

if TYPE_CHECKING:
    type _Condition = Callable[[], bool]
    type _KeyHandler[R] = Callable[[], R]
    type _EventHandler[R] = Callable[..., R]
    type _State[R] = tuple[Optional[_EventHandler[R]], Optional[_Condition]]

__all__ = ['use_key']

@hook
def use_key[R](*keys: str, condition: Union['_Condition', bool] = True) -> Callable[['_KeyHandler[R]'], '_KeyHandler[R]']:
    """
    Registra manejadores de eventos de teclado en el componente.
    
    Args:
        *keys: Combinación de teclas (ej: "enter", "c-c")
        condition: Condición para activar el binding (booleano o función)
        
    Returns:
        Decorador que recibe la función manejadora
        
    Ejemplo:
        @use_key('enter', condition=has_input)
        def handle_enter():
            print("Enter pressed")
    """
    tree = get_tree()
    component = tree.get_current_component()
    hook_index = component.state.get_index()
    state: '_State[R]' = component.state.get_slice( # type: ignore
        hook_index,
        default=(None, condition)
    )
    before_event_handler, before_condition = state

    def decorator(func: Callable[[], R]) -> Callable[[], R]:
        def event_handler(event: Any) -> R:
            return func()

        if before_event_handler != event_handler or (before_condition != None and before_condition != condition):
        
            if before_event_handler:
                component.key_bindings.remove(before_event_handler)
        
            filter_kb = Condition(condition) if callable(condition) else condition
            component.key_bindings.add(*keys, filter=filter_kb)(event_handler)

            component.state.set_slice(
                hook_index,
                value=(event_handler, condition if callable(condition) else None),
            )

        return func
    
    return decorator
