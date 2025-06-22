from unittest.main import main
from unittest import TestCase
from reactive.test_utils import mount
from reactive.components.button import Button, DEFAULT_TEXT


class TestButton(TestCase):
    def test_should_render(self):

        with mount(Button) as harness:
            harness.step(expect=True).find(DEFAULT_TEXT)
    
    def test_should_text(self):

        with mount(lambda: Button(text='MyButton')) as harness:
            harness.step(expect=True).find('MyButton').at(row=0)

    def test_should_styled(self):

        with mount(Button) as harness:
            harness.step(expect=True).find(DEFAULT_TEXT).at(row=0).bgcolor('aa0000').color('ffffff')

    def test_should_auto_width(self):
        text = 'Lorem ipsum dolor, sit amet consectetur'
        with mount(lambda: Button(text=text)) as harness:
            harness.step(expect=True).find(text).at(row=0)
    
    def test_should_hide_overflow(self):
        text = 'Lorem ipsum dolor, sit amet consectetur'
        width = 5 # text - symbols < >
        with mount(lambda: Button(text=text, width=width + 2)) as harness:
            first_part = harness.step(expect=True).find(text[:width]).at(row=0)
            first_part.right().not_text(text[width:])

if __name__ == '__main__':
    main().runTests()
