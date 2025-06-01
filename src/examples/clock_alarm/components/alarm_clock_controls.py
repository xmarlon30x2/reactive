from typing import Callable

from reactive import component, use_key
from prompt_toolkit.layout.containers import VSplit

from ..enums import Status
from .button_control import ButtonControl

__all__ = ['AlarmClockControls']

type _Action = Callable[[], None]

@component
def AlarmClockControls(on_reset: _Action, on_switch: _Action, status: 'Status'):
    @use_key('s')
    def handler_switch():
        on_switch()

    on_reset_enable = status == Status.STOP
    @use_key('r', condition=on_reset_enable)
    def handler_reset():
        on_reset()

    return VSplit([
        ButtonControl(
            text='start' if status == Status.STOP else 'stop',
            action=handler_switch
        ),
        ButtonControl(
            text='reset',
            action=handler_reset,
            disabled=not on_reset_enable
        )
    ])
