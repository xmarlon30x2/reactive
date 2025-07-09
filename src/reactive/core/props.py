from dataclasses import dataclass, field
from inspect import signature
from typing import Any, Callable, Optional, Tuple, TYPE_CHECKING

if TYPE_CHECKING:
    from ..types import Args, Kwargs

__all__ = ['Props', 'MAGIC_PROPS']


MAGIC_PROPS = ('id', 'key')

@dataclass
class Props:
    """
    Gestiona las propiedades (props) de un componente.
    
    Atributos:
        args: Argumentos posicionales
        kwargs: Argumentos clave
        _dirty: Indica si las props han cambiado
        
    Propiedades:
        key: Propiedad 'key' del componente
        id: Propiedad 'id' del componente
        dirty: Estado de modificación de las props
        
    Métodos:
        transform(func): Adapta props para pasarlas a la función render
        update(args, kwargs): Actualiza props y marca como modificadas
        cleanup(): Limpia el estado de modificación
    """
    args: 'Args'
    kwargs: 'Kwargs'
    _dirty: bool = field(default=False, init=False)
    
    @property
    def dirty(self) -> bool:
        return self._dirty

    @property
    def key(self) -> Optional[str]:
        return self.kwargs.get('key')

    @property
    def id(self) -> Optional[str]:
        return self.kwargs.get('id')

    def transform(self, func: Callable[..., Any]) -> Tuple['Args', 'Kwargs']:
        """
        Adapta las props para pasarlas a la función render.
        
        Args:
            func: Función render a la que se pasarán las props
            
        Returns:
            Tupla con (args, kwargs) preparados
            
        Note:
            Filtra props mágicas (id, key) a menos que la función las espere
        """
        parameters = signature(func).parameters
        kwargs = {key:value for (key,value) in self.kwargs.items() if key not in MAGIC_PROPS}
        if 'id' in parameters:
            kwargs['id'] = self.id
        if 'key' in parameters:
            kwargs['key'] = self.key
        return self.args, kwargs

    def update(self, args: 'Args', kwargs: 'Kwargs'):
        """
        Actualiza las props del componente.
        
        Args:
            args: Nuevos argumentos posicionales
            kwargs: Nuevos argumentos clave
            
        Returns:
            bool: True si hubo cambios
            
        Note:
            Marca el componente como dirty si las props cambiaron
        """
        if args != self.args:
            self.args = args
            self._dirty = True

        if kwargs != self.kwargs:
            self.kwargs = kwargs
            self._dirty = True

        return self._dirty

    def cleanup(self):
        """Limpia el estado de modificación de las props."""
        self._dirty = False
