from reactive import component
from prompt_toolkit.widgets import Label


@component
def AboutView():
    return [
        Label('Created by reactive team'),
        Label('Github: http://www.github.com/xmarlon30x2/reactive'),
    ]
