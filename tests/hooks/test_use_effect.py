from threading import Thread
from time import sleep
from typing import Callable
from unittest import TestCase
from src.reactive.hooks.use_state import use_state
from src.reactive import component, use_effect
from src.reactive.test_utils import mount

class TestUseReducer(TestCase):
    def test_use_effect_should_work(self):

        def long_task(callback: Callable[[int], None], n: int):
            sleep(3)
            callback(n)

        @component
        def MyComponent():
            count, set_count = use_state(0)
            
            @use_effect(count)
            def _():
                th = Thread(target=long_task, args=(set_count, count + 10))
                th.daemon = True
                th.start()

            return f'Count:{count}'

        with mount(MyComponent) as harness:
            count_query = lambda: harness.step(expect=True).find('Count:')
            count_query().right().text('0')
            sleep(3)
            count_query().right().text('10')
            sleep(4)
            count_query().right().text('20')
