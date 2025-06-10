from reactive import component, Button, use_state
from prompt_toolkit.widgets import Label
from prompt_toolkit.layout import HSplit

@component
def Boolean():
    bool, set_bool = use_state(False)

    return HSplit([
        Label('is true' if bool else 'is false'),
        Button(text='switch', handler=lambda: set_bool(not bool))
    ])
