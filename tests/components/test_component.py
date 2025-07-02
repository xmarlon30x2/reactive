from unittest import TestCase
from unittest.main import main
from prompt_toolkit.widgets import Button as ButtonPT
from src.reactive import component, Button
from src.reactive.types import Node
from src.reactive.test_utils import mount

class TestComponentDecorator(TestCase):
    def test_should_render_text(self):
        text = 'This is a component'
        
        @component
        def MyComponent():
            return text

        with mount(MyComponent) as harness:
            harness.step(expect=True).find(text).at(row=0)

    def test_should_render_container(self):
        text = 'This is a button'

        @component
        def MyComponent():
            return ButtonPT(text)

        with mount(MyComponent) as harness:
            harness.step(expect=True).find(text).at(row=0)

    def test_should_render_array_of_node(self):
        text = 'This is a text'
        button_text = 'This is a button'

        @component
        def MyComponent() -> list['Node']:
            return [
                text,
                Button(text=button_text)
            ]

        with mount(MyComponent) as harness:
            expect = harness.step(expect=True)

            label = expect.find(text).at(row=0)
            label.down().row().find(button_text)

if __name__ == '__main__':
    main().runTests()
