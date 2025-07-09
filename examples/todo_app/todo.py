from dataclasses import dataclass, field
from uuid import uuid4


@dataclass
class Todo:
    text: str
    id: str = field(default_factory=lambda: str(uuid4()))
