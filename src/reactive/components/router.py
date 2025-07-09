from typing import Any, Callable, Optional
from prompt_toolkit.layout.containers import AnyContainer

from ..hooks.use_navigation import use_navigation
from ..hooks.use_state import use_state
from ..router.context import RouterContextState, router_context
from ..router.views import is_view, is_layout_view, Views
from .provider import Provider
from .component import component

__all__ = ['Router']

@component
def _ResolveView(views: 'Views'):
    """
    Componente interno que resuelve la vista actual basada en la navegación.
    
    Args:
        views: Instancia de Views con la definición de vistas
        
    Returns:
        Contenedor de la vista renderizada
        
    Raises:
        RuntimeError: Si se detecta una estructura de vistas inválida
    """
    key, *_ = use_navigation()
    children: Optional[Callable[[], 'AnyContainer']] = None
    
    for view in reversed(views.get_trace(key)):
        if is_view(view):
            
            if children:
                raise RuntimeError(f'No se puede poner dos vistas anidadas: {key}')

            component = view['component']
            children = lambda: component(key)
        
        if is_layout_view(view):
            layout_key = view['key']

            if not children:
                raise RuntimeError(f'No se puede poner un layout sin una vista: {layout_key}')

            layout = view['layout']
            layout_children = children
            children = lambda: layout(layout_key, layout_children)

    if not children:
        return
    
    return children()

@component
def Router(
        views: 'Views',
        initial_key: str,
        initial_params: Optional[dict[str, Any]] = None
    ):
    """
    Componente Router para gestión de navegación en CLI.
    
    Args:
        views: Definición de vistas jerárquicas
        initial_key: Ruta inicial al montar el componente
        initial_params: Parámetros iniciales para la ruta
        
    Returns:
        Proveedor de contexto del enrutador con la vista resuelta
    """
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
