from typing import Callable, Optional
from reactive import Link, component
from reactive.types import Node
from prompt_toolkit.layout import HorizontalAlign, VSplit, AnyContainer


@component
def DashboardView(children: Callable[[], 'AnyContainer'], key: Optional[str] = None) -> Node:
    return [
        VSplit(
            [
                Link(text='Create todo', to='todo-edit'),
                Link(text='Todos', to='todo-history'),
                Link(text='About', to='about'),
            ],
            align=HorizontalAlign.CENTER,
            padding=1
        ),
        children(),
    ]
