from threading import Condition, Thread
from time import sleep
from typing import Any, Callable, TYPE_CHECKING, Literal, Self, overload
from prompt_toolkit.input import create_pipe_input, Input, PipeInput
from asyncio import run

from .expect.expect import Expect
from .output import TerminalOutput

if TYPE_CHECKING:
    from prompt_toolkit.output import Output
    from prompt_toolkit.application import Application
    from ..core.tree import Tree
    type _Create[R] = Callable[['TestHarness[R]', Input, Output], tuple[Application[R], Tree]]

__all__ = ['TestHarness']

class _Flag:
    def __init__(self):
        self.locked = False
        self.condition = Condition()

    def lock(self):
        with self.condition:
            self.locked = True

    def unlock(self):
        with self.condition:
            self.locked = False
            self.condition.notify_all()

    def wait(self):
        with self.condition:
            self.condition.wait_for(lambda: not self.locked)

class TestHarness[R]:
    def __init__(self, create: '_Create[R]'):
        self._create_app = create
        self._finished = False
        self._flag_start = _Flag()
        self._flag_end = _Flag()
        self._build_run = _Flag()
        
        self._thread = Thread(target=self._build)
        self._build_run.lock()
        self._thread.start()
        self._build_run.wait()

    def _before(self, app: Any):
        self._flag_start.wait()
        self._output.erase_screen()

    def _after(self, app: Any):
        self._flag_end.unlock()

    @property
    def input(self) -> 'PipeInput':
        return self._input
    
    def expect(self) -> 'Expect':
        terminal = self._output.capture()
        return Expect(_terminal=terminal)

    def get_screen(self) -> str:
        return self.expect().screen

    @property
    def is_finished(self) -> bool:
        return self._finished

    def _build(self):
        self._output = TerminalOutput()
        with create_pipe_input() as input:
            self._input = input
            self._app, self.tree = self._create_app(self, self._input, self._output)
            self._flag_start.lock()
            self._app.before_render.add_handler(self._before)
            self._app.after_render.add_handler(self._after)
            self._build_run.unlock()
            run(self._app.run_async())

    def close(self):
        self._finished = True
        if self._app.is_running:
            self._app.exit()
        self._flag_start.unlock()
        if self._thread.is_alive():
            self._thread.join()

    @overload
    def step(self, *, expect: Literal[False] = False, wait: float = 0.1, epochs: int = 1) -> None: ...
    @overload
    def step(self, *, expect: Literal[True], wait: float = 0.1, epochs: int = 1) -> 'Expect': ...

    def step(self, *, expect: bool = False, wait: float = 0.1, epochs: int = 1):
        assert epochs >= 1

        for _ in range(epochs):
            self._flag_end.lock()
            self._flag_start.unlock()
            self._flag_end.wait()
            self._flag_start.lock()

        sleep(wait)

        if expect:
            return self.expect()
        return

    def __enter__(self) -> Self:
        return self
    
    def __exit__(self, *args: Any):
        self.close()

    # def __del__(self):
    #     self.close()

