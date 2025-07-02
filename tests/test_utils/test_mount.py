from typing import Any
from unittest.mock import MagicMock
from src.reactive import component, use_state, use_key
from src.reactive.test_utils import mount
from prompt_toolkit.key_binding.key_bindings import KeyBindings
from unittest import TestCase
from unittest.main import main


class TestMount(TestCase):
    def test_mount_get_test_should_return_text(self):
        @component
        def MyLabel():
            return 'MyLabel'

        with mount(MyLabel) as harness:
            expect = harness.step(expect=True)
            expect.find('MyLabel').at(row=0, column=0)
            
            expect = harness.step(expect=True)
            expect.find('MyLabel').at(row=0, column=0)

    def test_mount_should_re_render_with_change_props(self):
        text = 'mylabel'

        @component
        def MyLabel(text: str):
            return text

        with mount(lambda: MyLabel(text=text)) as harness:
            expect = harness.step(expect=True)
            expect.find(text).at(row=0, column=0)
            
            text = 'other lab'
            expect = harness.step(expect=True)
            expect.find(text).at(row=0, column=0)

    def test_input_should_work(self):
        kb = KeyBindings()
        up = MagicMock()
        @kb.add('u')
        def _(e: Any):
            up()

        @component
        def StaticLabel():
            return 'static label'

        with mount(StaticLabel, key_bindings=kb) as harness:
            harness.step(expect=True).find('static label').at(row=0, column=0)
            harness.input.send_text('u')
            harness.step(expect=True).find('static label').at(row=0, column=0)
        
        up.assert_called_once()

    def test_mount_should_handle_input(self):
        @component
        def MyButton():
            count, set_count = use_state(0)
            
            @use_key('u')
            def _():
                set_count(count + 1)

            return f'hit me!({count})'

        with mount(MyButton) as harness:
            harness.step(expect=True).find('hit me!(0)').at(row=0)
            
            harness.step(expect=True).find('hit me!(0)').at(row=0)

            harness.input.send_text('u')
            harness.step(expect=True, epochs=2).find('hit me!(1)').at(row=0)

            harness.input.send_text('u')
            harness.step(expect=True, epochs=2).find('hit me!(2)').at(row=0)

            harness.step(expect=True).find('hit me!(2)').at(row=0)

if __name__ == '__main__':
    main().runTests()
