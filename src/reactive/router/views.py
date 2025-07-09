from typing import Callable, Optional, TypeGuard, TypedDict
from prompt_toolkit.layout.containers import AnyContainer

__all__ = ['create_views']

class View(TypedDict):
    """
    Vista simple con una clave y un componente.
    
    Atributos:
        key: Identificador único de la vista
        component: Función que renderiza la vista (recibe la clave actual)
    """
    key: str
    component: Callable[[str], 'AnyContainer']

class LayoutView(TypedDict):
    """
    Vista compuesta que contiene un layout y subvistas.
    
    Atributos:
        key: Identificador único del layout
        layout: Función que define la estructura (recibe clave y función de renderizado de subvistas)
        views: Lista de vistas o sub-layouts
    """
    key: str
    layout: Callable[[str, Callable[[], 'AnyContainer']], 'AnyContainer']
    views: list['LayoutView | View']

def is_view(obj: LayoutView | View) -> TypeGuard[View]:
    """
    Verifica si un objeto es una View simple.
    
    Args:
        obj: Objeto a verificar
        
    Returns:
        True si es una View, False si es un LayoutView
    """
    return set(obj.keys()) == set(('key', 'component'))

def is_layout_view(obj: LayoutView | View) -> TypeGuard[LayoutView]:
    """
    Verifica si un objeto es un LayoutView.
    
    Args:
        obj: Objeto a verificar
        
    Returns:
        True si es un LayoutView, False si es una View simple
    """
    return set(obj.keys()) == set(('key', 'views', 'layout'))

class Views:
    """
    Gestor de vistas jerárquicas para el enrutador.
    
    Args:
        views: Lista de definiciones de vistas (View o LayoutView)
        default_component: Componente a usar si no se encuentra una vista
    """
    def __init__(
            self,
            views: list['View | LayoutView'],
            default_component: Optional[Callable[[str], 'AnyContainer']] = None
        ):
        self.views = views
        self.default_component = default_component

    def get_trace(self, key: str) -> tuple['View | LayoutView', ...]:
        """
        Obtiene la ruta de vistas/layouts para una clave dada.
        
        Args:
            key: Clave de la vista a buscar
            
        Returns:
            Tupla con la jerarquía de vistas/layouts desde el padre hasta la vista objetivo
            
        Raises:
            ValueError: Si no se encuentra la vista y no hay componente predeterminado
        """
        def join(views: list['View | LayoutView']) -> Optional[tuple['View | LayoutView', ...]]:
            for view in views:
                view_key = view['key']
                
                if is_view(view) and view_key == key:
                    return (view, )
                
                if is_layout_view(view):
                    trace = join(views=view['views'])
                    if trace:
                        return (view, ) + trace
            
            return None

        trace = join(views=self.views)
        
        if not trace and self.default_component:
            return ({ 'key': key, 'component': self.default_component }, )

        if not trace:
            raise ValueError(f'No se ha encontrado una vista con la key: {key}')

        return trace

def create_views(
        views_defs: list['View | LayoutView'],
        default_component: Optional[Callable[[str], 'AnyContainer']] = None
    ) -> 'Views':
    """
    Factory para crear instancias de Views.
    
    Args:
        views_defs: Lista de definiciones de vistas
        default_component: Componente predeterminado para rutas no encontradas
        
    Returns:
        Instancia de Views configurada
    """

    return Views(
        views=views_defs,
        default_component=default_component
    )
