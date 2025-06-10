from reactive import (
    component,
    Router,
    Provider,
    use_state
)

from .todo import Todo
from .todos_context import TodosState, todos_context
from .views.views import views

@component
def TodoApp():
    todos, set_todos = use_state(list[Todo])
    
    def router():
        return Router(views=views, initial_key='home')
    
    return Provider(
        context=todos_context,
        value=TodosState(todos=todos, set_todos=set_todos),
        children=router
    )
