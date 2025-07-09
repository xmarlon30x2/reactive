from typing import Optional
from reactive import component
from prompt_toolkit.widgets import Label


@component
def NotFoundView(key: Optional[str] = None):
    return [
        Label('Error interno'),
        Label(f'no se encontro la vista: {key}')
    ]
