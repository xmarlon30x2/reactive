from contextlib import contextmanager
from os import environ
import sys

__all__ = ['args', 'env_vars']

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
