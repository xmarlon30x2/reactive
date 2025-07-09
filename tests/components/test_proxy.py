from unittest import TestCase
from src.reactive.test_utils import mount
from src.reactive import Proxy


class TestProxy(TestCase):
    def test_should_render(self):
        MyComponent = lambda: Proxy(node='hello world')

        with mount(MyComponent) as harness:
            harness.step(expect=True).find('hello world').at(row=0, column=0)
