from typing import Any, Callable
from unittest import TestCase
from src.reactive import component, use_memo
from src.reactive.test_utils import mount

class TestUseMemo(TestCase):
    def test_use_effect_should_work(self):
        
        def format_number(num: int):
            return f'Number:{num}'

        @component
        def MyComponent(num: int, tick: int):
            text = use_memo(lambda: format_number(num), tick)
            return text
        
        num = 0
        tick = 0
        
        with mount(lambda: MyComponent(num=num, tick=tick)) as harness:

            expect_num: Callable[[int], Any] = lambda num: harness.step(expect=True).find('Number:').right().text(str(num))

            expect_num(0)
            num = 1
            expect_num(0)
            num = 1
            expect_num(0)
            tick = 2
            expect_num(1)
