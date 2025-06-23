from prompt_toolkit.layout.containers import AnyContainer, HSplit, VSplit, VerticalAlign, HorizontalAlign

from .component import component

__all__ = ['Center']

@component
def Center(children: 'AnyContainer'):
    """
    Componente que centra su contenido hijo tanto vertical como horizontalmente.
    
    Args:
        children: Contenedor hijo a centrar
        
    Returns:
        Contenedor anidado con alineación central

    Ejemplo:
        Center(children=Label("Texto centrado"))
    """
    return HSplit([
        VSplit([
                children
            ],
            align=HorizontalAlign.CENTER
        )
        ],
        align=VerticalAlign.CENTER
    )
