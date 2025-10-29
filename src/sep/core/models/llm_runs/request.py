from __future__ import annotations
from dataclasses import dataclass, field
from datetime import datetime
from typing import List

from sep.core.models.llm_runs.evaluation import LLMEvaluatedQuestion

@dataclass
class LLMRequest:
    """Represents a single request made to the LLM."""
    json_version: float
    paper: str
    model: str
    temperature: float

    pdf_reader: bool
    pdf_reader_version: str
    process_mode: str

    raw_input: str
    raw_output: str

    run_id: int

    date: datetime = field(default_factory=datetime.utcnow)
    evaluated_questions: List[LLMEvaluatedQuestion] = field(default_factory=list)

    def add_question(self, question_id: str, answer: str, quote: str) -> LLMEvaluatedQuestion:
        """Adds a new evaluated question to the request."""
        question = LLMEvaluatedQuestion(
            id=question_id,
            answer=answer,
            quote=quote
        )
        self.evaluated_questions.append(question)
        return question