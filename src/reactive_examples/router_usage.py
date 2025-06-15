from dataclasses import dataclass, field
from typing import Callable, NamedTuple, Optional
from uuid import uuid4
from prompt_toolkit.widgets import Label
from prompt_toolkit.layout import AnyContainer, VSplit, HorizontalAlign, HSplit, VerticalAlign

from reactive import create_views, component, Button, Router, hook, Link
from reactive.hooks.use_state import StateSetter
from reactive.components.provider import Provider
from reactive.hooks.use_state import use_state
from reactive.hooks.use_context import use_context
from reactive.context import create_context

@dataclass
class Todo:
    text: str
    id: str = field(default_factory=lambda: str(uuid4()))

class TodosState(NamedTuple):
    todos: list[Todo]
    set_todos: Callable[[StateSetter[list[Todo]]], None]

todos_context = create_context(TodosState(
    todos = [],
    set_todos = lambda s: None # type: ignore
))

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

@component
def HomeView():
    return [
        Label('Todo app'),
        Link(text='Start', to='history')
    ]

@component
def AboutView():
    return [
        Label('Created by reactive team'),
        Label('Github: http://www.github.com/xmarlon30x2/reactive'),
    ]

@component
def NotFoundView(key: Optional[str] = None):
    return [
        Label('Error interno'),
        Label(f'no se encontro la vista: {key}')
    ]

@component
def ReadTodoView():
    params = use_params()
    todos = use_todos()
    id: str = params['id']
    index = todos.find(id)
    todo = todos[index]
    return [
        Label(todo.text),
        Link('Edit', to='edit', params={'id': id}),
        Link('Back', to=-1)
    ]
@component
def DashboardView(children: Callable[[], 'AnyContainer'], key: Optional[str] = None):
    return [
        VSplit(
            [
                Link(text='Create todo', to='edit'),
                Link(text='Todos', to='history'),
                Link(text='About', to='about'),
            ],
            align=HorizontalAlign.CENTER,
            padding=1
        ),
        children(),
    ]
    
views = create_views([
    {
        'key': 'home',
        'component': lambda key: HomeView(None, key)
    },
    {
        'key': 'about',
        'component': lambda key: AboutView(None, key)
    },
    {
        'key': 'todo-layout',
        'layout': lambda key, children: DashboardView(None, key, children=children),
        'views': [
            {
                'key': 'history',
                'component': lambda key: HistoryTodoView(None, key)
            },
            {
                'key': 'edit',
                'component': lambda key: EditTodoView(None, key)
            },
            {
                'key': 'read',
                'component': lambda key: ReadTodoView(None, key)
            }
        ]
    }
])


@component
def App():
    todos, set_todos = use_state(list[Todo])
    Provider(
        context=todos_context,
        value=TodosState(todos=todos, set_todos=set_todos),
        children=lambda: Router(views=views, start_key='home')
    )
