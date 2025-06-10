from reactive import Button, component, use_navigation
from reactive.types import Node
from ..components.todo_item import TodoItem
from ..hooks.use_todos import use_todos
from ..todo import Todo


@component
def HistoryTodoView() -> Node:
    todos = use_todos()
    navigation = use_navigation()

    def create_handler():
        new_todo = Todo(text='New todo')
        todos.save(new_todo)
        navigation.link('edit-todo', {'id': new_todo.id})

    return [
        [
            TodoItem(None, todo.id, todo=todo)
            for todo in todos.todos
        ],
        Button(text='Create', handler=create_handler)
    ]
