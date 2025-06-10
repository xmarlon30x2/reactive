from reactive.shortcuts import run_app, create_root
from reactive.key_bildings.focus import load_focus_tab
from .app import TodoApp

def main():
    root, kb = create_root(TodoApp)
    run_app(root, key_bindings=[kb, load_focus_tab()])

if __name__ == '__main__':
    main()
