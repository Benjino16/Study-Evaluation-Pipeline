from enum import Enum
from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional

class RunStatus(str, Enum):
    PENDING = "pending"
    RUNNING = "running"
    FINISHED = "finished"
    FAILED = "failed"
    CANCELLED = "cancelled"

@dataclass
class Run:
    id: str
    prompt: str
    model: str
    files: list[str]
    created_at: datetime = field(default_factory=datetime.utcnow)
    status: RunStatus = RunStatus.PENDING
    progress: float = 0.0
    message: Optional[str] = None
    result_path: Optional[str] = None
