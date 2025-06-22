from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Any, Callable

if TYPE_CHECKING:
    type _Effect = Callable[[], None]

__all__ = ['Effects']

@dataclass
class Effects:
    """
    Gestiona efectos secundarios asociados al ciclo de vida del componente.
    
    Atributos:
        _end_render: Lista de efectos a ejecutar después del render
        _unmount: Lista de efectos a ejecutar al desmontar
        
    Métodos:
        on_end_render(effect): Registra efecto post-render
        on_unmount(effect): Registra efecto de desmontaje
        execute_end_render(): Ejecuta todos los efectos post-render
        execute_unmount(): Ejecuta todos los efectos de desmontaje
    """
    _end_render: list['_Effect'] = field(default_factory=list[Any], init=False)
    _unmount: list['_Effect'] = field(default_factory=list[Any], init=False)

    def on_end_render(self, effect: '_Effect'):
        """
        Registra un efecto para ejecutar después del renderizado.
        
        Args:
            effect: Función sin argumentos a ejecutar
            
        Note:
            Se ejecutarán en el orden de registro
        """
        self._end_render.append(effect)
    
    def on_unmount(self, effect: '_Effect'):
        """
        Registra un efecto para ejecutar al desmontar el componente.
        
        Args:
            effect: Función sin argumentos a ejecutar
            
        Note:
            Ideal para limpieza de suscripciones o recursos
        """
        self._unmount.append(effect)

    def execute_end_render(self) -> None:
        """
        Ejecuta todos los efectos post-render registrados.
        
        Process:
            1. Ejecuta efectos en orden de registro
            2. Vacía la cola de efectos
        """
        while self._end_render:
            effect = self._end_render.pop(0)
            effect()
    
    def execute_unmount(self) -> None:
        """
        Ejecuta todos los efectos de desmontaje registrados.
        
        Process:
            1. Ejecuta efectos en orden de registro
            2. Vacía la cola de efectos
        """
        while self._unmount:
            effect = self._unmount.pop(0)
            effect()
