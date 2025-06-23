from typing import Callable, NamedTuple

from ..types import Reducer, Setter
from .use_state import use_state
from .hook import hook

__all__ = ['use_reducer']

class ReducerState[S, A](NamedTuple):
    state: S
    set_state: Callable[[A], S]

@hook
def use_reducer[S, A](reducer: 'Reducer[S, A]', initial_value: 'Setter[S] | S') -> 'ReducerState[S, A]':
    state, set_state = use_state(initial_value=initial_value)

    def handle_set_state(action: A) -> S:
        new_state = reducer(state, action)
        set_state(new_state)
        return new_state

    return ReducerState(state=state, set_state=handle_set_state)
