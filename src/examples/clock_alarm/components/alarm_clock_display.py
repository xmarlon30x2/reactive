from typing import Callable, Optional

from reactive import component, use_key, Proxy
from prompt_toolkit.layout.containers import HSplit, VSplit
from prompt_toolkit.widgets import Box, Button

from ..core import format_seconds
from ..enums import Status
from .text import Text

__all__ = ['AlarmClockDisplay']

@component
def AlarmClockDisplay(value: int = 0, on_change: Optional[Callable[[int], None]] = None, status: 'Status' = Status.STOP):
    def handler_on_change(delta: int):
        if on_change:
            on_change(max(0, value + delta))

    @use_key('s-up')
    def add_teen():
        handler_on_change(10)

    @use_key('up')
    def add_one():
        handler_on_change(1)

    @use_key('down')
    def subs_one():
        handler_on_change(-1)

    @use_key('s-down')
    def subs_teen():
        handler_on_change(-10)

    display_text = format_seconds(value)

    return HSplit([
        VSplit([
            Box(Text(text=display_text)),
            HSplit([
                Proxy(node=Button(text='-10s', handler=subs_teen)),
                Proxy(node=Button(text='-1s', handler=subs_one)),
                Proxy(node=Button(text='1s', handler=add_one)),
                Proxy(node=Button(text='10s', handler=add_teen))
            ])
        ]),
        Text(text="Running" if status == Status.START else 'Stoped')
    ])
