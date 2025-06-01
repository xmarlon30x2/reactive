from uuid import uuid4

from .hook import hook
from ..core.current import get_tree

__all__ = ['use_id']

def _generate_id() -> str:
    return str(uuid4())

@hook
def use_id() -> str:
    """
    Hook para crear id unicos, persistentes e inmutables
    
    Returns:
        id creado
    """
    tree = get_tree()
    component = tree.get_current_component()
    hook_index = component.state.get_index()
    id = component.state.get_slice(
        hook_index,
        default_factory=_generate_id
    )
    return id
