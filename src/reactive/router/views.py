from dataclasses import dataclass
from typing import Callable, Optional
from prompt_toolkit.layout.containers import AnyContainer

__all__ = ['ViewDef', 'ViewLayoutDef', 'ViewsDefs', 'create_views']

@dataclass
class ViewDef:
    key: str
    component: Callable[[str], 'AnyContainer'] # (key) -> AnyContainer

@dataclass
class ViewLayoutDef:
    key: str
    component: Callable[[str, Callable[[], 'AnyContainer']], 'AnyContainer'] # (key, component_func) -> AnyContainer
    views_defs: 'ViewsDefs'

type ViewsDefs = list[ViewLayoutDef | ViewDef]

class Views:
    def __init__(
            self,
            views_defs: 'ViewsDefs',
            default_component: Optional[Callable[[str], 'AnyContainer']] = None
        ):
        self.views_defs = views_defs
        self.default_component = default_component

    def get_trace(self, key: str) -> tuple['ViewLayoutDef | ViewDef', ...]:
        def join(views_defs: 'ViewsDefs') -> Optional[tuple['ViewLayoutDef | ViewDef', ...]]:
            for view_def in views_defs:
                if isinstance(view_def, ViewDef) and view_def.key == key:
                    return (view_def, )
                
                if isinstance(view_def, ViewLayoutDef):
                    trace = join(views_defs=view_def.views_defs)
                    if trace:
                        return (view_def, *trace)
            
            return None

        trace = join(views_defs=self.views_defs)
        
        if not trace and self.default_component:
            return (ViewDef(key=key, component=self.default_component), )

        if not trace:
            raise ValueError(f'No se ha encontrado una vista con la key: {key}')

        return trace

def create_views(
        views_defs: 'ViewsDefs',
        default_component: Optional[Callable[[str], 'AnyContainer']] = None
    ) -> 'Views':
    return Views(
        views_defs=views_defs,
        default_component=default_component
    )
