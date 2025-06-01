from prompt_toolkit.layout.containers import AnyContainer
from typing import Any, Callable, Dict, Iterable, Tuple, Union

type Args[T: Any = Any] = Tuple[T, ...]
type Kwargs[K: str = str, V = Any] = Dict[K, V]

type Node = Union[AnyContainer, str, None, Iterable['Node']]
type Computer[T] = Callable[[T], T]
type Setter[T] = Callable[[], T]
