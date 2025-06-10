from typing import Callable, Optional, TypeGuard, TypedDict
from prompt_toolkit.layout.containers import AnyContainer

__all__ = ['create_views']

class View(TypedDict):
    key: str
    component: Callable[[str], 'AnyContainer']

class LayoutView(TypedDict):
    key: str
    layout: Callable[[str, Callable[[], 'AnyContainer']], 'AnyContainer']
    views: list['LayoutView | View']

def is_view(obj: LayoutView | View) -> TypeGuard[View]:
    return set(obj.keys()) == set(('key', 'component'))

def is_layout_view(obj: LayoutView | View) -> TypeGuard[LayoutView]:
    return set(obj.keys()) == set(('key', 'views', 'layout'))

class Views:
    def __init__(
            self,
            views: list['View | LayoutView'],
            default_component: Optional[Callable[[str], 'AnyContainer']] = None
        ):
        self.views = views
        self.default_component = default_component

    def get_trace(self, key: str) -> tuple['View | LayoutView', ...]:
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
    
    return Views(
        views=views_defs,
        default_component=default_component
    )
