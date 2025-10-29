from __future__ import annotations
from dataclasses import dataclass, field, asdict
from datetime import datetime
from typing import Optional, List, Dict, Any

@dataclass(frozen=True)
class LLMEvaluatedQuestion:
    """Represents a single evaluated question within a request."""
    id: str
    answer: str
    quote: str