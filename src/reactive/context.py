class Context[T]:
    ...

def create_context[T](default_value: T) -> Context[T]:
    """
    Crea un nuevo contexto para compartir estado entre componentes
    
    Args:
        default_value: Valor por defecto del contexto
        
    Returns:
        Objeto contexto con métodos provide y use_context
    """
    raise NotImplementedError
