from typing import TYPE_CHECKING, Any, Optional
from prompt_toolkit.key_binding.key_bindings import KeyBindings, KeyBindingsBase
from prompt_toolkit.application.current import get_app
from prompt_toolkit.key_binding.bindings.focus import focus_next, focus_previous

if TYPE_CHECKING:
    from prompt_toolkit.layout.containers import AnyContainer

__all__ = ['load_recovery_focus', 'load_focus_tab']

DEFAULT_RECOVERY_KEY = 's-tab'

def load_recovery_focus(root_target: 'AnyContainer', key: Optional[str] = None) -> 'KeyBindingsBase':
    kb = KeyBindings()
    
    key = key or DEFAULT_RECOVERY_KEY
    @kb.add(key)
    def _(_: Any):
        app = get_app()
        app.layout.focus(root_target)

    return kb

def load_focus_tab():
    focus_kb = KeyBindings()
    focus_kb.add('s-tab')(focus_previous)
    focus_kb.add('tab')(focus_next)
    return focus_kb
