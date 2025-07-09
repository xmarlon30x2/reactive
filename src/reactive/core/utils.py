"""
Utilidades para el sistema de estado.

Funciones:
    is_compute(func): Verifica si una función es un "computer" (acepta estado actual)
    is_setter(func): Verifica si una función es un "setter" (sin argumentos)
    factory_value(value, value_factory): Produce nuevo valor usando:
        - Valor directo si no hay factory
        - Función computer si acepta un argumento
        - Función setter si no acepta argumentos
        - Valor original si no coincide

Uso típico:
    nuevo_valor = factory_value(estado_actual, actualizador)
"""
from inspect import signature
from typing import Any, TYPE_CHECKING, Callable, Optional, TypeGuard, Union

if TYPE_CHECKING:
    from ..types import Setter, Computer

def is_compute(func: Callable[..., Any]) -> TypeGuard['Computer[Any]']:
    """
    Determina si una función es un "computer" (acepta estado actual).
    
    Args:
        func: Función a verificar
        
    Returns:
        True si la función acepta exactamente 1 argumento
        
    Example:
        def update_count(current): return current + 1
        is_compute(update_count)  # True
    """
    return len(signature(func).parameters) == 1

def is_setter(func: Callable[..., Any]) -> TypeGuard['Setter[Any]']:
    """
    Determina si una función es un "setter" (sin argumentos).
    
    Args:
        func: Función a verificar
        
    Returns:
        True si la función no acepta argumentos
        
    Example:
        def generate_id(): return uuid4()
        is_setter(generate_id)  # True
    """
    return len(signature(func).parameters) == 0

def factory_value[S](value: S, value_factory: Optional['Union[Setter[S], Computer[S]]'] = None) -> S:
    """
    Produce un nuevo valor usando diferentes estrategias.
    
    Args:
        value: Valor actual
        value_factory: Función generadora del nuevo valor
        
    Returns:
        - value_factory(value) si es un computer
        - value_factory() si es un setter
        - value si no hay factory
        
    Example:
        factory_value(5, lambda x: x*2)  # 10
    """
    if not value_factory:
        return value
    if is_compute(value_factory):
        return value_factory(value)
    if is_setter(value_factory):
        return value_factory()
    return value
