from unittest import TestCase
from unittest.mock import MagicMock
from unittest.main import main
from reactive.router.views import Views, is_layout_view, is_view

class TestViews(TestCase):
    def test_get_trace_should_return_a_tuple_with_view(self):
        key = 'my-view'
        component = MagicMock()
        views = Views([
            {
                'key': key,
                'component': component
            }
        ])

        trace = views.get_trace(key=key)

        self.assertEqual(len(trace), 1)
        self.assertTrue(is_view(trace[0]))
        self.assertEqual(trace[0].get('key'), key)
        self.assertEqual(trace[0].get('component'), component)
        component.assert_not_called()
    
    def test_get_trace_should_return_a_correct_trace(self):
        views = Views([
            {
                'key': 'any-view',
                'component': MagicMock()
            },
            {
                'key': 'any-layout',
                'layout': MagicMock(),
                'views': [
                    {
                        'key': 'my-view',
                        'component': MagicMock()
                    }
                ]
            }
        ])

        trace = views.get_trace(key='my-view')

        self.assertEqual(len(trace), 2)
        
        layout = trace[0]
        self.assertTrue(is_layout_view(layout))
        self.assertEqual(layout.get('key'), 'any-layout')
        self.assertIsInstance(layout.get('layout'), MagicMock)
        layout['layout'].assert_not_called() # type: ignore

        view = trace[1]
        self.assertTrue(is_view(view))
        self.assertEqual(view.get('key'), 'my-view')
        self.assertIsInstance(view.get('component'), MagicMock)
        view['component'].assert_not_called() # type: ignore

if __name__ == '__main__':
    main().runTests()
