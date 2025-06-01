from reactive.key_bildings.focus import load_focus_tab
from reactive.shortcuts import run_app, create_root
from .app import AlarmClock

__all__ = ['main']


def main():
    container, container_key_bindings = create_root(
        lambda : AlarmClock()
    )
    
    run_app(
        container,
        key_bindings=[
            container_key_bindings,
            load_focus_tab()
        ],
        refresh_interval=0.7
    )


if __name__ == '__main__':
    main()
