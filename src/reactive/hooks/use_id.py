from uuid import uuid4

from .hook import hook
from ..core.current import get_tree

__all__ = ['use_id']

def _generate_id() -> str:
    return str(uuid4())

@hook
def use_id() -> str:
    """
    Genera un ID único persistente durante la vida del componente.
    
    Útil para asociar elementos en la interfaz o identificar componentes.
    
    Returns:
        ID único generado
        
    Ejemplo:
        id = use_id()
        # → "3b9f5c7a-1d3f-4a8c-9f7b-6d2e8c1a4f7b"
    """
    tree = get_tree()
    component = tree.get_current_component()
    hook_index = component.state.get_index()
    id = component.state.get_slice(
        hook_index,
        default_factory=_generate_id
    )
    return id
