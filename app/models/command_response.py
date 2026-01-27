from dataclasses import dataclass, field
from typing import Any, Dict, List

@dataclass
class CommandResponse:
    messages: List[Dict[str, Any]]
    routing: Dict[str, Any]
    errors: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)