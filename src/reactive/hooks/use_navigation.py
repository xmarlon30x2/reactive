from typing import Any, Callable, NamedTuple, Optional
from ..router.context import router_context
from .hook import hook
from .use_context import use_context

__all__ = ['use_navigation']


class Navigation(NamedTuple):
    key: str
    """Key de la vista actual"""
    params: dict[str, Any]
    """Parametros"""
    link: Callable[[str, Optional[dict[str, Any]]], None]
    to: Callable[[int], None]
    """Permite desplazarse por el historial"""
    has_next: bool
    """Si tiene una ruta siguiente en el historial"""
    has_previous: bool
    """Si tiene una ruta anterior en el historial"""

@hook
def use_navigation() -> Navigation:
    """
    Returns:
        NamedTuple(Navigation):
            name: Key de la vista actual.
            params: Parametros de la vista actual.
    """
    router_state = use_context(router_context)
    
    if not router_state:
        raise RuntimeError('No se puede usar use_navigation fuera del contexto del router')
    
    history_index, history_keys, history_params, update = router_state
    entrys = len(history_params)

    key = history_keys[history_index]
    params = history_params[history_index]
    has_previous = history_index > 0
    has_next = history_index < entrys - 1

    def link(new_key: str, new_params: Optional[dict[str, Any]] = None) -> None:
        if key == new_key and params == new_params:
            return
        
        new_params = new_params or {}
        
        if entrys - 1 == history_index:
            new_history_keys = [*history_keys, new_key]
            new_history_params = [*history_params, new_params]
            new_index = history_index + 1
        
        else:
            new_history_keys = history_keys[:history_index + 1]
            new_history_keys.append(new_key)
            new_history_params = history_params[:history_index + 1]
            new_history_params.append(new_params)
            new_index = len(new_history_keys) - 1

        update(new_index, new_history_keys, new_history_params)
    
    def to(n: int) -> None:
        new_index = min(max(n + history_index, 0), entrys - 1)
        
        if new_index != history_index:
            update(new_index, history_keys, history_params)

    return Navigation(
        key=key,
        params=params,
        has_previous=has_previous,
        has_next=has_next,
        link=link,
        to=to
    )
