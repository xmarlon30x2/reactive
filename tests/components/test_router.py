from typing import Any, Callable
from unittest import TestCase
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

    def test_should_render_layout(self):
        
        @component
        def Home():
            return 'home page'

        @component
        def Layout(children: Callable[[], Node]) -> Node:
            return [
                'layout text',
                children()
            ]

        views = create_views([
            {
                'layout': lambda key, children: Layout(None, key, children=children),
                'key': 'layout',
                'views': [
                    {
                        'key': 'home',
                        'component': lambda key: Home(None, key)
                    }
                ]
            }
        ])
        
        @component
        def MyApp():
            return Router(views=views, initial_key='home')

        with mount(MyApp) as harness:
            expect = harness.step(expect=True, epochs=2)
            expect.find('layout text').at(row=0, column=0).down().text('home page')
