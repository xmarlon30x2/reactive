from .component import component
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ..types import Node

__all__ = ['Proxy']

@component
def Proxy[N: 'Node'](node: N) -> N:
    return node
