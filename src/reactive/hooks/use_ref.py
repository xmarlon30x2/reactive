from typing import Callable, Optional, Tuple, TYPE_CHECKING, Union

from ..core.current import get_tree
from .hook import hook

if TYPE_CHECKING:
    from ..types import Setter, Computer

__all__ = ['use_ref']

type RefSetter[S] = Union['Setter[S]', 'Computer[S]', S]

@hook
def use_ref[S](initial_value: Optional[Union['Setter[S]', S]] = None) -> Tuple[S, Callable[[RefSetter[S]], None]]:
    """
    Crea una referencia mutable que no causa re-renders.
    
    Args:
        initial_value: Valor inicial o función generadora
        
    Returns:
        Tupla con:
        - Valor actual de la referencia
        - Función para actualizar la referencia
        
    Ejemplo:
        count_ref, set_count_ref = use_ref(0)
        set_count_ref(5)  # Actualiza sin causar re-render
    """
    tree = get_tree()
    component = tree.get_current_component()
    hook_index = component.state.get_index()
    is_callable = callable(initial_value)
    ref = component.state.get_slice(
        hook_index,
        default=initial_value if not is_callable else None,
        default_factory=initial_value if is_callable else None # type: ignore
    )
    
    def set_ref(new_ref: Union['Setter[S]', 'Computer[S]', S]) -> None:
        nonlocal component, hook_index
        is_callable = callable(new_ref)
        component.state.set_slice(
            index=hook_index,
            value=new_ref if not is_callable else None,
            value_factory=new_ref if is_callable else None # type: ignore
        )

    return ref, set_ref
