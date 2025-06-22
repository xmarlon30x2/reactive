from typing import Any

from .use_ref import use_ref
from ..types import Setter

__all__ = ['use_memo']

def use_memo[V](factory: Setter[V], *dependencies: Any) -> V:
    """
    Memoiza un valor computacionalmente costoso.
    
    Solo recalcula el valor cuando cambian las dependencias.
    
    Args:
        factory: Función que computa el valor
        *dependencies: Dependencias que activan el recálculo
        
    Returns:
        Valor memoizado
        
    Ejemplo:
        result = use_memo(lambda: expensive_computation(a, b), a, b)
    """
    value, set_value = use_ref(factory) # type: ignore
    last_dependencies, set_last_dependencies = use_ref(dependencies)

    if last_dependencies != dependencies:
        value = factory()
        set_value(value)
        set_last_dependencies(dependencies)

    return value
