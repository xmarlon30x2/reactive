from .component import component
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ..types import Node

__all__ = ['Proxy']

@component
def Proxy[N: 'Node'](node: N) -> N:
    """
    Componente Proxy que renderiza un nodo directamente.
    
    Args:
        node: Nodo a renderizar (puede ser cualquier elemento renderizable)
        
    Returns:
        El mismo nodo de entrada sin modificaciones
    """
    return node
