from typing import Callable, Optional, Tuple, TYPE_CHECKING, TypeVar, Union

from ..core.current import get_tree
from .hook import hook

if TYPE_CHECKING:
    from ..types import Setter, Computer

__all__ = ['use_state']

type StateSetter[S] = Union['Setter[S]', 'Computer[S]', S]
S = TypeVar('S')

@hook
def use_state(initial_value: Optional[Union[S, 'Setter[S]']] = None) -> Tuple[S, Callable[[StateSetter[S]], None]]:
    """
    Gestiona estado local que dispara re-renders al actualizarse.
    
    Args:
        initial_value: Valor inicial o función generadora
        
    Returns:
        Tupla con:
        - Valor actual del estado
        - Función para actualizar el estado
        
    Ejemplo:
        count, set_count = use_state(0)
        set_count(5)  # Actualiza y causa re-render
    """
    tree = get_tree()
    component = tree.get_current_component()
    hook_index = component.state.get_index()
    is_callable = callable(initial_value)
    state = component.state.get_slice(
        hook_index,
        default=initial_value if not is_callable else None,
        default_factory=initial_value if is_callable else None # type: ignore
    )
    
    def set_state(new_state: Union['Setter[S]', 'Computer[S]', S]) -> None:
        nonlocal component, hook_index
        is_callable = callable(new_state)
        component.state.set_slice(
            index=hook_index,
            value=new_state if not is_callable else None,
            value_factory=new_state if is_callable else None # type: ignore
        )
        component.set_dirty()

    return state, set_state
