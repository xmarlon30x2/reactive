from reactive import component, Link, Router, create_views, create_root, run_app
from reactive.types import Node

@component
def View1() -> Node:
    return [
        "View 1",
        Link(text='Go to view 2',to='view2')
    ]

@component
def View2() -> Node:
    return [
        "View 2",
        Link(text='Back to view 1',to='view1')
    ]

views = create_views([
    {
        'key': 'view1',
        'component': lambda key: View1(None, key)
    },
    {
        'key': 'view2',
        'component': lambda key: View2(None, key)
    }
])

@component
def App():
    return Router(views=views, initial_key='view1')

def main():
    root, kb = create_root(App)
    run_app(root, key_bindings=kb)

if __name__ == '__main__':
    main()
