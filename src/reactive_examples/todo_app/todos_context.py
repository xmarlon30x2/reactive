from typing import Callable, NamedTuple
from reactive import create_context
from reactive.hooks.use_state import StateSetter

from .todo import Todo

class TodosState(NamedTuple):
    todos: list[Todo]
    set_todos: Callable[[StateSetter[list[Todo]]], None]

todos_context = create_context(TodosState(
    todos = [],
    set_todos = lambda s: None # type: ignore
))
