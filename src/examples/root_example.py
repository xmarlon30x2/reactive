from reactive import create_root
from component import Boolean

root, key_bindings = create_root(Boolean())
run_app(root, key_bindings=key_bindings)
