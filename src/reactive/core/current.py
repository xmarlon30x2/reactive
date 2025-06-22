"""
Gestión del contexto del árbol de componentes mediante ContextVars.

Funciones:
    get_tree_or_none(): Obtiene el árbol actual o None
    get_tree(): Obtiene el árbol actual (error si no existe)
    push_tree(tree): Establece un nuevo árbol como actual
    pop_tree(token): Restaura el árbol anterior
    open_tree(tree): Context manager para operar en un árbol

Uso típico:
    with open_tree(my_tree):
        # Operaciones dentro del contexto del árbol
        component.render()
"""
from contextlib import contextmanager
from contextvars import ContextVar, Token

from typing import TYPE_CHECKING, Optional, Union

if TYPE_CHECKING:
    from .tree import Tree

_trees: ContextVar[Optional['Tree']] = ContextVar('_trees', default=None)

def get_tree_or_none() -> Optional['Tree']:
    """
    Obtiene el árbol de componentes actual si existe.
    
    Returns:
        El árbol actual o None si no se ha establecido
        
    Note:
        Versión segura de get_tree() que no lanza excepciones
    """
    global _trees
    return _trees.get()

def get_tree() -> 'Tree':
    """
    Obtiene el árbol de componentes actual obligatoriamente.
    
    Returns:
        El árbol actual
        
    Raises:
        RuntimeError: Si no hay ningún árbol establecido
        
    Example:
        current_tree = get_tree()
    """
    global _trees
    tree = _trees.get()
    if not tree:
        raise RuntimeError('No se ha establecido ningun arbol')
    return tree

def push_tree(tree: 'Tree') -> Token[Union['Tree', None]]:
    """
    Establece un nuevo árbol como contexto actual.
    
    Args:
        tree: Árbol a establecer como actual
        
    Returns:
        Token que puede usarse para restaurar el estado anterior
        
    Note:
        Usar junto con pop_tree para gestión adecuada del contexto
    """
    global _trees
    return _trees.set(tree)

def pop_tree(token: 'Token[Union[Tree, None]]'):
    """
    Restaura el árbol de componentes anterior.
    
    Args:
        token: Token obtenido al hacer push_tree
        
    Example:
        token = push_tree(new_tree)
        # operaciones...
        pop_tree(token)
    """
    global _trees
    _trees.reset(token)

@contextmanager
def open_tree(tree: 'Tree'):
    """
    Context manager para operar dentro del contexto de un árbol específico.
    
    Args:
        tree: Árbol de componentes que se establecerá como contexto actual
        
    Yields:
        None
        
    Example:
        with open_tree(my_tree):
            # Operaciones dentro del contexto de my_tree
    """
    token = push_tree(tree)
    try:
        yield

    finally:
        pop_tree(token)
