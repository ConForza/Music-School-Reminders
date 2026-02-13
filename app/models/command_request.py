from dataclasses import dataclass, field
from typing import Any, Dict, Optional

@dataclass
class CommandRequest:
    command: str
    source_id: str
    args: Dict[str, Any] = field(default_factory=dict)
    routing: Dict[str, Any] = field(default_factory=dict)
    principal_id: Optional[int] = None
