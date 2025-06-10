from typing import Any

from .use_ref import use_ref
from ..types import Setter

__all__ = ['use_memo']

def use_memo[V](factory: Setter[V], *deps: Any) -> V:
    value, set_value = use_ref(factory) # type: ignore
    last_deps, set_last_deps = use_ref(deps)

    if last_deps != deps:
        value = factory()
        set_value(value)
        set_last_deps(deps)

    return value

