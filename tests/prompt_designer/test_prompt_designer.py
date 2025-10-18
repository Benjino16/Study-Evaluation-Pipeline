# tests/test_prompt_designer.py
import types
import pytest
from unittest.mock import patch

from sep.prompt_designer import run_prompt_design

def test_get_paper_with_index_wraps():
    papers = ["a.pdf", "b.pdf", "c.pdf"]
    assert run_prompt_design._get_paper_with_index(papers, 0) == "a.pdf"
    assert run_prompt_design._get_paper_with_index(papers, 3) == "a.pdf"
    assert run_prompt_design._get_paper_with_index(papers, 4) == "b.pdf"

@pytest.mark.parametrize("index,n,expected", [
    (0, 2, ["a.pdf", "b.pdf"]),
    (1, 2, ["b.pdf", "c.pdf"]),
    (2, 2, ["c.pdf", "a.pdf"]),
    (0, 5, ["a.pdf", "b.pdf", "c.pdf"]),  # n > len -> capped
])
def test_get_number_of_papers(index, n, expected):
    papers = ["a.pdf", "b.pdf", "c.pdf"]
    assert run_prompt_design._get_number_of_papers(papers, index, n) == expected


