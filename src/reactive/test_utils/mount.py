from typing import Any, Callable, Optional, TYPE_CHECKING

from prompt_toolkit.application import Application
from prompt_toolkit.widgets import Label
from prompt_toolkit.key_binding import DynamicKeyBindings, KeyBindingsBase, merge_key_bindings
from prompt_toolkit.layout import DynamicContainer, Layout, AnyContainer

from ..constants import DEFAULT_REFRESH_INTERVAL
from ..core.current import open_tree
from ..core.tree import Tree
from .test_harness import TestHarness

if TYPE_CHECKING:
    from prompt_toolkit.input import Input
    from prompt_toolkit.output import Output

__all__ = ['mount']

def mount(
        component: Callable[[], 'AnyContainer'], *,
        key_bindings: Optional['KeyBindingsBase'] = None,
        refresh_interval: Optional[float] = None
        ) -> 'TestHarness[Any]':

    def create(harness: 'TestHarness[Any]', input: 'Input', output: 'Output'):
        nonlocal key_bindings, refresh_interval
        tree = Tree()
        def get_container():
            nonlocal tree, harness
            
            if harness.is_finished:
                return Label('TestHarness is finished')

            with open_tree(tree):
                container = component()
                tree.flip()
            return container

        root = DynamicContainer(get_container)

        def get_key_bindings():
            nonlocal key_bindings
            tree_kb = tree.key_bindings
            if tree_kb and key_bindings:
                return merge_key_bindings([tree_kb, key_bindings])
            return tree_kb or key_bindings
        
        root_kb: KeyBindingsBase = DynamicKeyBindings(get_key_bindings)
        
        refresh_interval = refresh_interval or DEFAULT_REFRESH_INTERVAL
        app = Application[Any](
            layout=Layout(root),
            input=input,
            output=output,
            refresh_interval=refresh_interval,
            key_bindings=root_kb
        )
        return app, tree
    return TestHarness(create=create)
