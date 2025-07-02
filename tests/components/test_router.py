from typing import Any, Callable
from unittest import TestCase
from unittest.main import main
from reactive.components.link import Link
from reactive import component, create_views, Router
from reactive.types import Node
from reactive.test_utils import mount

class TestRouter(TestCase):
    def test_router_should_render_text(self):

        @component
        def Start() -> Node:
            return [
                'Start Page',
                Link(text='To end', to='end')
            ]

        @component
        def End() -> Node:
            return [
                'End',
                Link(text='To start', to=-1)
            ]

        views = create_views([
            {'key': 'start', 'component': lambda key: Start(None, key)},
            {'key': 'end', 'component': lambda key: End(None, key)}
        ])

        @component
        def MyApp():
            return Router(initial_key='start', views=views)

        with mount(MyApp) as harness:
            query: Callable[[str, str, int], Any] = lambda header, button, epochs: harness.step(expect=True, epochs=epochs).find(header).at(row=0, column=0).down().row().find(button)
            query('Start Page', 'To end', 2)
            harness.input.send_text('\r')
            query('End', 'To start', 2)
            harness.input.send_text('\r')
            query('Start Page', 'To end', 2)

if __name__ == '__main__':
    main().runTests()
