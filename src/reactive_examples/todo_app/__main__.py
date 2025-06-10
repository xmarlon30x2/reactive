from reactive.shortcuts import run_app, create_root
from .app import TodoApp

def main():
    root, kb = create_root(TodoApp)
    run_app(root, key_bindings=kb)

if __name__ == '__main__':
    main()
