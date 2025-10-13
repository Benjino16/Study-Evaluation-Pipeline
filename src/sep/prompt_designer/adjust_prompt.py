from sep.utils.load_json import load_json
from sep.api_request.gemini_pipeline import process_file_with_gemini
from sep.prompt_designer.get_correct_answers import get_correct_answers
import sys

PATH_TO_PROMPT_DESIGNER = r"D:\dev\github\Study-Evaluation-Pipeline\resources\prompt_designer.json"

def adjust_prompt(old_prompt: str, paper: str, model: str, temp: float) -> str:
    """This method adjusts a given prompt based on the paper's content."""

    prompt_dict = load_json(PATH_TO_PROMPT_DESIGNER)
    correct_answers = get_correct_answers(paper)

    prompt_designer_prompt = prompt_dict["prompt"]
    new_prompt = process_file_with_gemini(prompt_designer_prompt + "\n\nPrompt: " + old_prompt + "\n\nCorrect Answers: " + correct_answers.strip(), paper, model, temp)

    return new_prompt