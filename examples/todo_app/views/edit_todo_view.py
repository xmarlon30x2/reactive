from reactive import Link, component, use_effect, use_navigation
from reactive.types import Node
from prompt_toolkit.widgets import TextArea
from ..hooks.use_todos import use_todos
from ..todo import Todo


@component
def EditTodoView() -> Node:
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

    text_area = TextArea(
        text=todo.text,
        height=6,
        scrollbar=True,
        multiline=True
    )

    def handler_save():
        todo = Todo(id=id, text=text_area.text)
        todos.save(todo)

    return [
        text_area,
        Link(
            text='Save',
            to='todo-read',
            handler=handler_save,
            params={'id': todo.id}
        )
    ]
