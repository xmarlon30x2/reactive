from reactive import component, Link
from reactive.types import Node
from prompt_toolkit.widgets import Label


@component
def AboutView() -> Node:
    return [
        Label('Created by reactive team'),
        Label('Github: http://www.github.com/xmarlon30x2/reactive'),
        Link(text='Back', to=-1)
    ]
