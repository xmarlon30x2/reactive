from typing import Callable
from reactive import Link, component, Button, use_navigation
from reactive.types import Node
from prompt_toolkit.layout import HorizontalAlign, VSplit, AnyContainer

from ..hooks.use_todos import use_todos
from ..todo import Todo


@component
def DashboardView(children: Callable[[], 'AnyContainer']) -> Node:
    todos = use_todos()
    navigation = use_navigation()

    def create_handler():
        new_todo = Todo(text='New todo')
        todos.save(new_todo)
        navigation.link('todo-edit', {'id': new_todo.id})

    return [
        VSplit(
            [
                Button(text='Create todo', handler=create_handler),
                Link(text='Todos', to='todo-history'),
                Link(text='About', to='about'),
            ],
            align=HorizontalAlign.CENTER,
            padding=1
        ),
        children(),
    ]
