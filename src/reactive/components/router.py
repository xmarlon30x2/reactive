from typing import Any, Callable, Optional
from prompt_toolkit.layout.containers import AnyContainer

from ..hooks.use_navigation import use_navigation
from ..hooks.use_state import use_state
from ..router.context import RouterContextState, router_context
from ..router.views import ViewDef, ViewLayoutDef, Views
from .provider import Provider
from .component import component

__all__ = ['Router']

@component
def _ResolveView(views: 'Views'):
    key, *_ = use_navigation()
    last_view_def: Optional[Callable[[], 'AnyContainer']] = None
    
    for view_def in reversed(views.get_trace(key)):
        if isinstance(view_def, ViewDef):
            if last_view_def:
                raise RuntimeError(f'No se puede poner dos vistas anidadas: {view_def.key}')
            
            view_component = view_def.component
            view_key = view_def.key
            last_view_def = lambda: view_component(view_key)
        
        if isinstance(view_def, ViewLayoutDef):
            if not last_view_def:
                raise RuntimeError(f'No se puede poner un layout sin una vista: {view_def.key}')
            layout_component = view_def.component
            layout_key = view_def.key
            child_component = last_view_def
            last_view_def = lambda: layout_component(
                layout_key,
                child_component
            )

    if not last_view_def:
        return
    
    return last_view_def()

@component
def Router(
        views: 'Views',
        initial_key: str,
        initial_params: Optional[dict[str, Any]] = None
    ):
    state, set_state = use_state((int(0), [initial_key], [initial_params or {}]))
    history_index, history_keys, history_params = state
    
    def update(
            new_index: int,
            new_history_keys: list[str],
            new_history_params: list[dict[str, Any]],
            ):
        lenght_params = len(new_history_params)
        lenght_keys = len(new_history_keys)
        assert lenght_params == lenght_keys, 'No coinciden el tamaño del historial de parametros con el de keys'
        assert new_index < lenght_params, 'Indice de historial fuera de rango'
        assert new_index >= 0, 'Indice de historial fuera de rango'
        set_state((new_index, new_history_keys, new_history_params))
    
    value = RouterContextState(
        history_index=history_index,
        history_params=history_params,
        history_keys=history_keys,
        update=update
    )
    return Provider(
        value=value,
        children=lambda: _ResolveView(views=views),
        context=router_context
    )
