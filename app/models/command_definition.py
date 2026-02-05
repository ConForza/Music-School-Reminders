from dataclasses import dataclass
from typing import Callable, List

@dataclass
class CommandDefinition:
    required_args: List[str]
    handler: Callable
    access: str
    default_preview: bool=True