from threading import Thread
from time import sleep
from typing import Any, Callable
from unittest import TestCase
from prompt_toolkit.application import Application
from prompt_toolkit.layout import Layout, AnyContainer
from prompt_toolkit.input.defaults import create_pipe_input
from src.reactive.test_utils.output import TerminalOutput
from src.reactive.test_utils.expect import Expect
from src.reactive import create_root, component
from src.reactive.core.current import open_tree
from src.reactive.core.tree import Tree

class TestCreateRoot(TestCase):
    def _expect_from_root(self, root: AnyContainer, tree: Tree):
        output = TerminalOutput()
        with create_pipe_input() as inp:
            with open_tree(tree):
                app = Application[None](layout=Layout(root), input=inp, output=output)
                thread = Thread(target=app.run, daemon=True)
                thread.start()
                sleep(1)
                app.exit()
                thread.join()
        return Expect(output.capture())

    def test_create_root_render(self):
        @component
        def MyLabel():
            return 'my label'

        root, _, tree = self._create_root_with_tree(MyLabel)
        expect = self._expect_from_root(root, tree)
        expect.find('my label')

    def test_create_root_with_fallback(self):
        from prompt_toolkit.layout.containers import Window
        @component
        def Broken():
            raise ValueError('fail!')

        def fallback(key: str, exc: Exception):
            return Window(content=None, height=1, char=f'error: {exc}')

        root, _, tree = self._create_root_with_tree(Broken, fallback=fallback)
        expect = self._expect_from_root(root, tree)
        expect.find('error: fail!')

    def test_create_root_with_recover_focus_key(self):
        @component
        def MyLabel():
            return 'focus test'

        root, kb, tree = self._create_root_with_tree(MyLabel, recover_focus_key='f2')
        self.assertIsNotNone(kb)
        expect = self._expect_from_root(root, tree)
        expect.find('focus test')

    def _create_root_with_tree(self, component_func: Callable[[], AnyContainer], **kwargs: Any):
        from src.reactive.core.tree import Tree
        tree = Tree()
        result = create_root(component_func, tree_instance=tree, **kwargs)
        return (*result, tree)
