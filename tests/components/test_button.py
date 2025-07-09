from unittest import TestCase
from src.reactive.components.component import component
from src.reactive.test_utils import mount
from src.reactive.components.button import Button, DEFAULT_TEXT, LEFT_SYMBOL_DISABLED, RIGHT_SYMBOL_DISABLED, LEFT_SYMBOL, RIGHT_SYMBOL


class TestButton(TestCase):
    def test_should_render(self):

        with mount(Button) as harness:
            harness.step(expect=True).find(DEFAULT_TEXT)
    
    def test_should_text(self):
        with mount(lambda: Button(text='MyButton')) as harness:
            harness.step(expect=True).find(f'{LEFT_SYMBOL}MyButton{RIGHT_SYMBOL}').at(row=0)

    def test_should_styled(self):

        with mount(Button) as harness:
            harness.step(expect=True).find(DEFAULT_TEXT).at(row=0).bgcolor('af0000').color('ffffff')

    def test_should_auto_width(self):
        text = 'Lorem ipsum dolor, sit amet consectetur'
        with mount(lambda: Button(text=text)) as harness:
            harness.step(expect=True).find(text).at(row=0)
    
    def test_should_hide_overflow(self):
        text = 'Lorem ipsum dolor, sit amet consectetur'
        width = 5
        
        @component
        def MyApp():
            return Button(
                text = text,
                width = width + len(LEFT_SYMBOL) + len(RIGHT_SYMBOL)
            )

        with mount(MyApp) as harness:
            first_part = harness.step(expect=True).find(text[:width]).at(row=0)
            first_part.right().not_text(text[width:])

    def test_should_auto_set_width(self):
        text = 'hello'+ ''.join((str(x) for x in range(30)))
        with mount(lambda: Button(text=text, width=None)) as harness:
            hello = harness.step(expect=True).find('hello')
            numbers_visibles = hello.right().text(text[5: 28])
            numbers_visibles.right().text(RIGHT_SYMBOL)

    def test_should_render_disabled_symbols(self):
        with mount(lambda: Button(text='hello world', left_symbol='/', right_symbol='\\', disable=True)) as harness:
            harness.step(expect=True).find(f'{LEFT_SYMBOL_DISABLED}hello world{RIGHT_SYMBOL_DISABLED}').at(row=0)

    def test_should_render_custom_symbols(self):
        with mount(lambda: Button(text='hello world', left_symbol='/', right_symbol='\\')) as harness:
            harness.step(expect=True).find(f'/hello world\\').at(row=0)

    def test_should_render_custom_disabled_symbols(self):
        with mount(lambda: Button(text='hello world', disable=True, left_symbol='/', right_symbol='\\', right_symbol_disabled='}', left_symbol_disabled='{')) as harness:
            harness.step(expect=True).find('{hello world}').at(row=0)

