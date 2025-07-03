from unittest import TestCase
from src.reactive import component, use_reducer, use_key
from src.reactive.test_utils import mount, Expect

def expect_result(expect: 'Expect', text: str) -> None:
    expect.find('Count:').at(row=0, column=0).right().text(text)

def counter_reducer(state: int, action: str):
    match action:
        case 'add':
            return state + 1
        case 'sub':
            return state - 1
        case _:
            return state

class TestUseReducer(TestCase):
    def test_use_reducer_should_work(self):
        
        @component
        def MyComponent():
            state, update = use_reducer(counter_reducer, 0)
            
            @use_key('a')
            def _():
                update('add')
            
            @use_key('s')
            def _():
                update('sub')

            return f'Count:{state}'

        with mount(MyComponent) as harness:

            expect_result(harness.step(expect=True, epochs=2), text='0')
            harness.input.send_text('a')
            expect_result(harness.step(expect=True, epochs=2), '1')
            harness.input.send_text('ss')
            expect_result(harness.step(expect=True, epochs=2), '-1')
            expect_result(harness.step(expect=True), '-1')
            expect_result(harness.step(expect=True), '-1')
            expect_result(harness.step(expect=True), '-1')
    
    def test_use_reducer_should_accept_setter_in_initial_value(self):
        @component
        def MyComponent():
            state, _ = use_reducer(counter_reducer, lambda: 12)
            return f'Count:{state}'

        with mount(MyComponent) as harness:
            expect_result(harness.step(expect=True), text='12')
