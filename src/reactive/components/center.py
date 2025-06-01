from prompt_toolkit.layout.containers import AnyContainer, HSplit, VSplit, VerticalAlign, HorizontalAlign

from .component import component

__all__ = ['Center']

@component
def Center(children: 'AnyContainer'):
    return HSplit([
        VSplit([
                children
            ],
            align=HorizontalAlign.CENTER
        )
        ],
        align=VerticalAlign.CENTER
    )
