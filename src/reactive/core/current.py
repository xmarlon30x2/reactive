from contextlib import contextmanager
from contextvars import ContextVar, Token

from typing import TYPE_CHECKING, Optional, Union

if TYPE_CHECKING:
    from .tree import Tree

_trees: ContextVar[Optional['Tree']] = ContextVar('_trees', default=None)

def get_tree_or_none() -> Optional['Tree']:
    global _trees
    return _trees.get()

def get_tree() -> 'Tree':
    global _trees
    tree = _trees.get()
    if not tree:
        raise RuntimeError('No se ha establecido ningun arbol')
    return tree

def push_tree(tree: 'Tree') -> Token[Union['Tree', None]]:
    global _trees
    return _trees.set(tree)

def pop_tree(token: 'Token[Union[Tree, None]]'):
    global _trees
    _trees.reset(token)

@contextmanager
def open_tree(tree: 'Tree'):
    token = push_tree(tree)
    try:
        yield

    finally:
        pop_tree(token)
