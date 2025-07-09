from reactive import component
from prompt_toolkit.layout.containers import HSplit, HorizontalAlign, VSplit, VerticalAlign, AnyContainer
from prompt_toolkit.widgets import Frame

__all__ = ['AlarmClockFrame']

@component
def AlarmClockFrame(display: 'AnyContainer', controls: 'AnyContainer'):
    return VSplit([
        HSplit([
                Frame(
                    HSplit([
                        display,
                        controls
                    ]),
                    title='Reloj Alarma'
                )
            ],
            align=VerticalAlign.CENTER
        )],
        align=HorizontalAlign.CENTER
    )
