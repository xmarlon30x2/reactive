from typing import Any, Callable, NamedTuple, Optional

from ..context import Context, create_context

__all__: list[str] = []

class RouterContextState(NamedTuple):
    """
    Estado del contexto de enrutamiento para aplicaciones CLI.
    
    Contiene:
        history_index: Índice actual en el historial de navegación
        history_keys: Lista de claves de rutas visitadas
        history_params: Lista de parámetros asociados a cada ruta
        update: Función para actualizar el estado del enrutador
    """
    history_index: int
    history_keys: list[str]
    history_params: list[dict[str, Any]]
    update: Callable[[int, list[str], list[dict[str, Any]]], None]

router_context: Context[Optional[RouterContextState]] = create_context(None)
