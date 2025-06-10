from typing import Callable, NamedTuple
from reactive import hook, use_context
from ..todo import Todo
from ..todos_context import todos_context


class Todos(NamedTuple):
    todos: list[Todo]
    save: Callable[[Todo], None]
    find: Callable[[str], int]

@hook
def use_todos() -> Todos:
    todos, set_todos = use_context(todos_context)

    def find(id: str) -> int:
        for index, todo in enumerate(todos):
            if todo.id == id:
                return index
        return -1

    def save(new_todo: Todo):
        index = find(new_todo.id)
        new_todos = [*todos]

        if index == -1:
            new_todos.append(new_todo)
        else:
            new_todos[index] = new_todo

        set_todos(new_todos)

    return Todos(todos=todos, save=save, find=find)
