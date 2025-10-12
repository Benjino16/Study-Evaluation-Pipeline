import random
from sep.prompt_designer.adjust_prompt import adjust_prompt
#from sep.api_request.request_manager import run_request
from sep.utils.load_json import load_json
from sep.prompt_designer.json_log import init_log, update_log

PATH_TO_BASIC_PROMPT = r"D:\dev\github\Study-Evaluation-Pipeline\resources\base_prompt.json"

def run_prompt_designer(base_prompt_json: str, loop: int, papers: list[str]):
    prompt_design_prompt = load_json(base_prompt_json)["prompt"]
    current_prompt = "base prompt"
    paper = _get_paper_with_index(papers, 0)
    current_accuracy = _evaluate_prompt(current_prompt, paper)

    init_log({
        "prompt_design_prompt": prompt_design_prompt,
        "base_prompt": current_prompt,
        "papers": papers,
        "tested_papers": papers,
        "base_accuracy": current_accuracy,
    })

    for i in range(loop):
        paper = _get_paper_with_index(papers, i)
        adj_prompt = adjust_prompt(current_prompt, paper)
        accuracy = _evaluate_prompt(adj_prompt, paper)

        update_log({
            "input_prompt": current_prompt,
            "adjusted_prompt": adj_prompt,
            "paper_used_for_adjustment": paper,
            "tested_papers": papers,
            "accuracy": accuracy,
        })

        if accuracy >= current_accuracy:
            current_prompt = adj_prompt
            current_accuracy = accuracy


def _get_paper_with_index(papers: list[str], index: int) -> str:
    """Get the paper at the specified index."""
    return papers[index % len(papers)]

def _evaluate_prompt(prompt: str, paper: str) -> float:
    """Test the prompt using all papers and return the accuracy."""
    #raw_answer = run_request(paper, "gemini-pro-2.5", True, False, 0, 1.0)
    return random.random()


if __name__ == "__main__":
    run_prompt_designer(PATH_TO_BASIC_PROMPT, 3, [r"D:\dev\github\Study-Evaluation-Pipeline\data\input\pdfs\main\0005.pdf", r"D:\dev\github\Study-Evaluation-Pipeline\data\input\pdfs\main\0013.pdf"])
