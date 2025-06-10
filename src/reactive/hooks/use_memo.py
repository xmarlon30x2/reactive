from typing import Any

from .use_ref import use_ref
from ..types import Setter

__all__ = ['use_memo']

def use_memo[V](factory: Setter[V], *dependencies: Any) -> V:
    """
    Hook para memoizar valores computacionalmente costosos
    
    Args:
        compute_func: Función que computa el valor
        dependencies: Lista de dependencias que activan el recálculo
        
    Returns:
        Valor memoizado
    """
    value, set_value = use_ref(factory) # type: ignore
    last_dependencies, set_last_dependencies = use_ref(dependencies)

    if last_dependencies != dependencies:
        value = factory()
        set_value(value)
        set_last_dependencies(dependencies)

    return value

