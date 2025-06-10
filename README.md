Un ejemplo de un componente
```python
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

```
Y como lo uso?
```
from reactive import create_root, run_app
from .component import Boolean

root, key_bindings = create_root(Boolean)
run_app(root, key_bindings=key_bindings)
```
