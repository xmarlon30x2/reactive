from reactive import Link, component
from reactive.types import Node
from prompt_toolkit.widgets import Label


@component
def HomeView() -> 'Node':
    return [
        Label('Todo app'),
        Link(text='Start', to='todo-history')
    ]
