from sep.utils.load_json import load_json
from sep.api_request.gemini_pipeline import process_file_with_gemini
from sep.prompt_designer.get_correct_answers import get_correct_answers
from sep.env_manager import PROMPT_DESIGN_PROMPT_PATH

PROMPT_DESIGN_PROMPT = load_json(PROMPT_DESIGN_PROMPT_PATH)["prompt"]

def adjust_prompt(old_prompt: str, paper: str, model: str, temp: float) -> str:
    """This method adjusts a given prompt based on the paper's content."""

    correct_answers = get_correct_answers(paper)
    new_prompt = process_file_with_gemini(PROMPT_DESIGN_PROMPT + "\n\nPrompt: " + old_prompt + "\n\nCorrect Answers: " + correct_answers.strip(), paper, model, temp)

    return new_prompt