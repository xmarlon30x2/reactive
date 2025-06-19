from typing import List
from unittest import TestCase
from prompt_toolkit.widgets import Button
from src.reactive import component
from src.reactive.types import Node
from reactive.test_utils.mount import mount

class TestComponentDecorator(TestCase):
    def test_should_render_text(self):        
        text = 'This is a component'
        
        @component
        def MyComponent():
            return text

        with mount('component.screen', MyComponent) as harness:
            harness.step()
            
            self.assertIn(text, harness.get_text())

    def test_should_render_container(self):
        text = 'This is a button'

        @component
        def MyComponent():
            return Button(text)

        with mount('component.screen', MyComponent) as harness:
            harness.step()
            
            self.assertIn(text, harness.get_text())

    def test_should_render_array_of_node(self):
        text = 'This is a text'
        label_text = 'This is a label'

        @component
        def MyComponent() -> List['Node']:
            return [
                text,
                Button(label_text)
            ]

        with mount('component.screen', MyComponent) as harness:
            harness.step()

            screen = harness.get_text()
            text_index = screen.find(text)
            label_text_index = screen.find(label_text)
            self.assertNotEqual(text_index, -1)
            self.assertNotEqual(label_text_index, -1)
            self.assertGreaterEqual(label_text_index, text_index + len(text))
