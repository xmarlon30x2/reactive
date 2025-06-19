import sys
from contextlib import contextmanager
from os import environ
from typing import Optional

from ..core.tree import Tree
from ..core.component import Component
from ..core.current import get_tree

__all__ = ['args', 'env_vars', 'print_tree', 'print_component']

@contextmanager
def args(*argv: str):
    """
    Context manager para simular sys.argv.
    """
    old_argv = sys.argv
    sys.argv = list(argv)
    try:
        yield
    finally:
        sys.argv = old_argv

def env_vars(**kwargs: str):
    """
    Context manager para simular variables de entorno sin afectar el sistema.
    """
    original = {key:environ.get(key) for key in kwargs}
    environ.update({key: value for key,value in kwargs.items()})
    try:
        yield
    finally:
        for key,value in original.items():
            if value is None:
                environ.pop(key, None)
            else:
                environ[key] = value

def _format_level(ident: int):
    return '    ' * ident

def print_tree(tree: Optional[Tree] = None, level: int = 0):
    tree = tree or get_tree()
    print(f'{_format_level(level)}Tree')
    for index, base in enumerate(tree.bases):
        print_component(tree=tree, component=base, level=level, index=index)

def print_component(tree: Tree, component: 'Component', index: Optional[int] = None, level: int = 0):
    current_string = '<-' if tree.get_current_component_or_none() == component else ''
    rel_string = f'{component.props.key}:' if component.props.key else f'{index}:' if index != None else ''
    id_string = f'({component.props.id})' if component.props.id else ''
    dirty_string = '*' if component.dirty else ''
    print(
        f'{_format_level(level)}{rel_string}{component.name}{id_string}{dirty_string}{current_string}')
    for children_index, children in enumerate(component.relations.childrens):
        print_component(tree=tree, component=children, level=level+1, index=children_index)
