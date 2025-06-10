from typing import Optional
from unittest import TestCase

from src.reactive.components.component import component
from src.reactive.test_utils.test_harness import TestHarness, mount

class TestComponentDecorator(TestCase):
    harness: Optional['TestHarness[None]'] = None

    def setup(self):
        self.harness = None

    def teardown(self):
        if self.harness:
            self.harness.clear_buffers()

    def test_should_render_text(self):        
        text = 'This is a component'
        
        @component
        def MyComponent():
            return text

        with mount('my_component.screen', MyComponent) as harness:
            harness.step()
            
            self.assertIn(text, harness.get_text())

