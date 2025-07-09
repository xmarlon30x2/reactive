from asyncio import sleep
from reactive import component, use_state, use_effect
from prompt_toolkit.application import get_app

from .components.alarm_clock_frame import AlarmClockFrame
from .components.alarm_clock_controls import AlarmClockControls
from .components.alarm_clock_display import AlarmClockDisplay
from .core import sound_alarm
from .enums import Status

__all__ = ['AlarmClock']

@component
def AlarmClock(start_value: int = 0, start_state: Status = Status.STOP):
    seconds, set_seconds = use_state(initial_value=start_value)
    status, set_status = use_state(initial_value=start_state)

    def on_change(new_seconds: int):
        set_seconds(new_seconds)
    
    def on_reset():
        set_status(start_state)
        set_seconds(start_value)
    
    def on_switch():
        set_status(lambda status: Status.STOP if status == Status.START else Status.START)

    @use_effect(status, seconds)
    def _():
        if status == Status.START:
            app = get_app()

            async def update_seconds_task():
                await sleep(1)
                new_seconds = max(0, seconds-1)
                set_seconds(new_seconds)

                if new_seconds == 0:
                    set_status(Status.STOP)
                    app.create_background_task(sound_alarm())

            task = app.create_background_task(update_seconds_task())
            return lambda: task.cancel()

    return AlarmClockFrame(
        display=AlarmClockDisplay(value=seconds, on_change=on_change, status=status),
        controls=AlarmClockControls(
            on_reset=on_reset,
            on_switch=on_switch,
            status=status
        )
    )

