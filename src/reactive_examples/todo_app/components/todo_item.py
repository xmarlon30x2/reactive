from reactive import Link, component
from reactive.types import Node
from ..todo import Todo


@component
def TodoItem(todo: Todo) -> Node:
    text = todo.text if len(todo.text) < 20 else todo.text[:20]+'...'
    return Link(text=text, to='read-todo', params={'id': todo.id})
