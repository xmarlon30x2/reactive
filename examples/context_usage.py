from typing import Callable
from reactive import (
    component,
    Button,
    create_context,
    use_context,
    Provider,
    use_state,
    create_root,
    run_app
)
from reactive.hooks.use_state import StateSetter
from reactive.key_bildings import load_focus_tab
from prompt_toolkit.widgets import Label
from prompt_toolkit.layout import HSplit

type ContextType = tuple[int, Callable[[StateSetter[int]], None]]
_default_state: ContextType = (int(0), lambda c: None)
count_context = create_context(_default_state)

@component
def AddButton():
    count, set_count = use_context(count_context)
    return Button(text='Add', handler=lambda: set_count(count+1))

@component
def SubsButton():
    count, set_count = use_context(count_context)
    return Button(text='Subs', handler=lambda: set_count(count-1))

@component
def CountDisplay():
    count, _ = use_context(count_context)
    return Label(text=f'Count {count}')

@component
def Layout():
    return HSplit([
        CountDisplay(),
        AddButton(),
        SubsButton(),
    ])

@component
def App():
    value = use_state(0)
    return Provider(
        value=value,
        children=Layout,
        context=count_context
    )

def main():
    root, kb = create_root(App)
    run_app(
        root,
        key_bindings=[kb, load_focus_tab()]
    )

if __name__ == '__main__':
    main()
