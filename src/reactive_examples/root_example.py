from reactive import create_root, run_app, component, Button, use_state
from reactive.key_bildings import load_focus_tab
from prompt_toolkit.widgets import Label
from prompt_toolkit.layout import HSplit

@component
def Boolean():
    bool, set_bool = use_state(False)

    return HSplit([
        Label('is true' if bool else 'is false'),
        Button(text='switch', handler=lambda: set_bool(not bool))
    ])

def main():
    root, key_bindings = create_root(Boolean)
    run_app(
        root,
        key_bindings=[key_bindings, load_focus_tab()]
    )

if __name__ == '__main__':
    main()
