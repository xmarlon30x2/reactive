from functools import wraps
from typing import Any, Callable, ParamSpec, TypeVar

from ..core.current import get_tree

P = ParamSpec('P')
R = TypeVar('R')

def hook(func: Callable[P, R]) -> Callable[P, R]:
    @wraps(func)
    def decorator(*args: P.args, **kwargs: P.kwargs) -> Any:
        tree = get_tree()
        component = tree.get_current_component()
        
        try:
            result = func(*args, **kwargs)
        
        finally:
            component.state.increment_index()

        return result

    return decorator
