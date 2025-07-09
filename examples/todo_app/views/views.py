from reactive import create_views
from .edit_todo_view import EditTodoView
from .history_todo_view import HistoryTodoView
from .read_todo_view import ReadTodoView
from .todo_not_found import TodoNotFound
from .about_view import AboutView
from .home_view import HomeView
from .dashboard_view import DashboardView


views = create_views([
    {
        'key': 'home',
        'component': lambda key: HomeView(None, key)
    },
    {
        'key': 'about',
        'component': lambda key: AboutView(None, key)
    },
    {
        'key': 'todo-layout',
        'layout': lambda key, children: DashboardView(None, key, children=children),
        'views': [
            {
                'key': 'todo-history',
                'component': lambda key: HistoryTodoView(None, key)
            },
            {
                'key': 'todo-edit',
                'component': lambda key: EditTodoView(None, key)
            },
            {
                'key': 'todo-read',
                'component': lambda key: ReadTodoView(None, key)
            },
            {
                'key': 'todo-not-found',
                'component': lambda key: TodoNotFound(None, key)
            }
        ]
    }
])
