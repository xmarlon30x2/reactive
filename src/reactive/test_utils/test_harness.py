from pathlib import Path
from threading import Thread
from time import sleep
from typing import Any, Callable, Generic, Literal, Optional, TYPE_CHECKING, Self, TypeVar
from prompt_toolkit.output import create_output, Output
from prompt_toolkit.input import create_pipe_input, Input
from prompt_toolkit.application import Application
from prompt_toolkit.layout import Layout
from prompt_toolkit.key_binding import merge_key_bindings, KeyBindingsBase

from ..core.tree import Tree
from ..shortcuts import create_root

if TYPE_CHECKING:
    from prompt_toolkit.layout.containers import AnyContainer

V = TypeVar('V')

class _AppThread[R](Thread):
    _value: R

    def __init__(self, app: 'Application[R]'):
        self.app = app
        self._end = False
        super().__init__(daemon=True, target=self.target)

    def target(self):
        self._end = False
        try:
            self._value = self.app.run()
        finally:
            self._end = True

    def terminate(self):
        self.app.exit()
        if self.is_alive():
            self.join()
        return self.value

    @property
    def value(self):
        if not self.end:
            raise RuntimeError('No se ha establecido un valor')
        return self._value

    @property
    def end(self) -> bool:
        return self._end and not self.is_alive()

type _CreateApp[S] = Callable[[Input, Output, float], Application[S]]

class TestHarness(Generic[V]):
    output_filename: str
    tree: 'Tree'
    _input_buffer: str
    _create_app: _CreateApp[V]
    _runner: Optional[_AppThread[V]] = None

    def __init__(self, output_filename: str, create_app: _CreateApp[V], tree: 'Tree'):
        self._create_app = create_app
        self.tree = tree
        self._input_buffer = ''
        self.output_filename = output_filename

    @property
    def return_value(self) -> V:
        if not self._runner:
            raise RuntimeError('No se ejecutado la aplicacion')
        return self._runner.value

    @property
    def status(self) -> Literal['running', 'pause']:
        return 'pause' if self._runner and self._runner.end else 'running'

    def step(
            self,
            timeout: Optional[float] = None,
            refresh_interval: Optional[float] = None
        ) -> None:        
        refresh_interval = refresh_interval or 0.1
        timeout = timeout or refresh_interval

        with open(self.output_filename, 'w') as file_output:
            with create_pipe_input() as input:
                output = create_output(file_output)
                input.send_text(self._input_buffer)
                self._input_buffer = ''
                app = self._create_app(input, output, refresh_interval)
                self._runner = _AppThread(app=app)
                self._runner.start()
                sleep(timeout)
                self._runner.terminate()
    
    def get_text(self) -> str:
        """
        Devuelve todo lo que se ha renderizado incluyendo el codigo ANSI
        """
        try:
            with open(self.output_filename, 'r') as file_output:
                return file_output.read()
        except FileNotFoundError:
            return ''

    def clear_buffers(self) -> None:
        """
        Limpia el contendio acumulado en el buffer de salida y entrada
        """
        output_path = Path(self.output_filename)
        try:
            output_path.unlink(True)
        except PermissionError:
            pass
        self._input_buffer = ''

    def send_text(self, text: str) -> None:
        """
        Envia un texto al input
        """
        self._input_buffer += text

    def __enter__(self) -> Self:
        return self
    
    def __exit__(self, *args: Any):
        self.close()

    def __del__(self):
        self.close()
    
    def close(self):
        if self._runner and self.status == 'running':
            self._runner.terminate()
        self.clear_buffers()

def mount(
        output_filename: str,
        component_func: Callable[[], 'AnyContainer'],
        key_bindings: Optional['KeyBindingsBase'] = None
        ):
    tree = Tree()
    
    root, kb = create_root(component_func, tree_instance=tree)
    key_bindings = merge_key_bindings([kb, key_bindings]) if key_bindings else kb

    def create_app(input: Input, output: Output, refresh_interval: float):
        return Application[Any](
            layout=Layout(root),
            input=input,
            output=output,
            refresh_interval=refresh_interval,
            key_bindings=key_bindings
        )
    return TestHarness(output_filename, create_app=create_app, tree=tree)
