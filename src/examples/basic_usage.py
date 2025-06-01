from reactive import component, use_state, use_key, run_app, create_root, load_focus_tab, Center, Button
from prompt_toolkit.widgets import Label, Frame, HorizontalLine
from prompt_toolkit.layout import HSplit, WindowAlign

@component
def Counter():
    count, set_count = use_state(0)
    
    # Key binding para incrementar con flecha arriba
    @use_key("up")
    def increment():
        set_count(count + 1)
    
    # Key binding para decrementar con flecha abajo
    @use_key("down")
    def decrement():
        set_count(max(0, count - 1))
    
    return Center(
        children=Frame(
            HSplit([
                Label(text=f"[ Count: {count} ]", align=WindowAlign.CENTER),
                Button(text="add", handler=increment),
                Button(text="substract", handler=decrement),
                HorizontalLine(),
                Label(text="Press tab to change focus"),
                Label(text="enter to click"),
                Label(text="up to add"),
                Label(text="down to substract"),
            ])
        )
    )

# Punto de entrada de la aplicación
root, kb = create_root(Counter)
run_app(root, key_bindings=[
    kb,
    load_focus_tab()
])
