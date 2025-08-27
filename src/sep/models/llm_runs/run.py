from __future__ import annotations
from dataclasses import dataclass, field, asdict
from datetime import datetime
from typing import Optional, List, Dict, Any

from sep.models.llm_runs.request import LLMRequest

@dataclass
class LLMRun:
    """Represents a single run of the LLM evaluation process."""
    id: int
    model: str
    temperature: float
    date: datetime = field(default_factory=datetime.utcnow)

    pdf_reader: bool
    pdf_reader_version: str
    process_mode: str

    raw_input: str

    requests: List[LLMRequest] = field(default_factory=list)


    def add_request(self, request: LLMRequest) -> LLMRequest:
        """Adds a new request to the run."""
        self.requests.append(request)
        return request
    
    def to_dict(self) -> Dict[str, Any]:
        """Converts the LLMRun instance to a dictionary."""
        d = asdict(self)
        d['date'] = self.date.isoformat()
        return d