from reactive import Link, component, use_effect, use_navigation
from reactive.types import Node
from prompt_toolkit.widgets import Frame, Label
from ..hooks.use_todos import use_todos


@component
def ReadTodoView() -> Node:
    navigation = use_navigation()
    todos = use_todos()

    id = navigation.params.get('id', 'unknow')
    index = todos.find(id)
    todo = todos.todos[index] if index != -1 else None

    @use_effect(todo)
    def _():
        if todo == None:
            navigation.link('todo-not-found', {'id': id})

    if not todo:
        return None

    return [
        Frame(
            Label(text=todo.text)
        ),
        Link(text='Edit', to='todo-edit', params={'id': id}),
        Link(text='Back', to=-1)
    ]
