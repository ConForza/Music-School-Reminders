from dataclasses import dataclass
from typing import Any, Dict, List, Optional

@dataclass
class CommandExecution:
    id: Optional[int]
    timestamp: str
    command: str
    source_id: str
    args: Dict[str, Any]
    result_type: str
    routing: Optional[Dict[str, Any]]
    errors: List[str]
    status: str