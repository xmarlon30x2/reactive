from typing import Any, TYPE_CHECKING, Optional, Union

from .utils import factory_value

if TYPE_CHECKING:
    from ..types import Setter, Computer

__all__ = ['State']


class State:
    """
    Gestiona el estado interno de un componente mediante "slices".
    
    Cada hook (useState, useEffect, etc) ocupa un slice de estado.
    
    Métodos:
        get_slice(index): Obtiene valor de un slice de estado
        set_slice(index): Actualiza valor de un slice
        get_index(): Obtiene el índice del próximo hook
        active_hook(): Incrementa el contador de hooks
        cleanup(): Limpia slices no utilizados
        
    Comportamiento:
        - Mantiene un diccionario de slices por índice
        - Los hooks se registran secuencialmente durante el render
        - Solo persisten los slices utilizados en el último render
    """
    _slices: dict[int, Any]

    def __init__(self):
        self._slices = {}
        self._active_indexs = -1

    def get_slice[S](self,
                        index: int,
                        default: Optional[S] = None,
                        default_factory: 'Optional[Setter[S]]' = None
                    ) -> Any:
        """
        Obtiene un slice de estado por su índice.
        
        Args:
            index: Índice del slice
            default: Valor por defecto si no existe
            default_factory: Función generadora del valor por defecto
            
        Returns:
            Valor actual del slice
            
        Note:
            Si el slice no existe, lo crea con el valor por defecto
        """
        if not index in self._slices:
            new_slice = default_factory() if default_factory else default
            self._slices[index] = new_slice
            return new_slice

        return self._slices[index]

    def set_slice(self,
                    index: int,
                    value: Optional[Any] = None, 
                    value_factory: 'Optional[Union[Setter[Any], Computer[Any]]]' = None
                ):
        """
        Actualiza un slice de estado.
        
        Args:
            index: Índice del slice a actualizar
            value: Nuevo valor directo
            value_factory: Función generadora del nuevo valor
            
        Note:
            Prefiere value_factory si está presente
        """
        current_slice = self._slices.get(index, None)
        self._slices[index] = value if not value_factory else factory_value(current_slice, value_factory)

    def get_index(self) -> int:
        """
        Obtiene el índice actual para el próximo hook.

        Returns:
            Índice numérico que será asignado al próximo hook

        Note:
            Incrementa automáticamente con cada llamada a active_hook()
        """
        return self._active_indexs

    def active_hook(self) -> None:
        """
        Incrementa el contador de hooks activos.
        
        Note:
            Se llama automáticamente al usar el decorador @hook
        """
        self._active_indexs += 1

    def cleanup(self) -> None:
        """
        Limpia los slices de estado no utilizados.
        
        Process:
            1. Elimina slices con índice mayor al contador actual
            2. Reinicia el contador de hooks
        """
        for index in list(self._slices.keys()):
            if not index <= self._active_indexs:
                self._slices.pop(index)
        self._active_indexs = -1

