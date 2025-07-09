from reactive import component
from reactive.types import Node
from prompt_toolkit.widgets import Label
from prompt_toolkit.layout import WindowAlign
from ..components.todo_item import TodoItem
from ..hooks.use_todos import use_todos


@component
def HistoryTodoView() -> Node:
    todos = use_todos()

    return [
        TodoItem(None, todo.id, todo=todo)
        for todo in todos.todos
    ] + (
        [Label('Not has todos', align=WindowAlign.CENTER)]
        if not todos.todos else []
    )
