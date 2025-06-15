from typing import Any, Callable, NamedTuple, Optional

from ..context import Context, create_context

__all__: list[str] = []

class RouterContextState(NamedTuple):
    history_index: int
    history_keys: list[str]
    history_params: list[dict[str, Any]]
    update: Callable[[int, list[str], list[dict[str, Any]]], None]

router_context: Context[Optional[RouterContextState]] = create_context(None)
