import argparse
import time

from sep.env_manager import DEFAULT_CSV, BASIC_PROMPT_PATH
from sep.evaluation.load_saved_json import load_saved_jsons
from sep.prompt_designer.adjust_prompt import adjust_prompt, PROMPT_DESIGN_PROMPT
from sep.process_paper import process_paper
from sep.prompt_manager import getPrompt
from sep.utils.load_json import load_json
from sep.prompt_designer.json_log import init_log, update_log
from sep.evaluation.compare_answers import compare_data
from sep.logger import setup_logger

log = setup_logger(__name__)

def run_prompt_designer(base_prompt_json: str, loop: int, test_paper: int, papers: list[str], model: str, temp: float,  csv: str, delay: int = 5):
    """
    Executes a prompt design loop that iteratively adjusts a base prompt using given
    parameters to improve accuracy based on test papers.

    Parameters:
    base_prompt_json (str): Path to the JSON file containing the base prompt configuration.
    loop (int): Number of iterations for prompt adjustment.
    test_paper (int): Number of papers to be tested at each iteration.
    papers (list[str]): List of paper identifiers used for testing and adjusting the prompt.
    model (str): Identifier of the model used for prompt adjustment.
    temp (float): Temperature parameter for controlling randomness during prompt adjustment.
    csv (str): Path to the CSV file where evaluation results are stored.
    """

    if len(papers) == 0:
        raise ValueError("No papers provided for prompt design.")
    if loop < 1:
        raise ValueError("Loop parameter must be at least 1.")
    if test_paper < 1:
        raise ValueError("Test paper parameter must be at least 1.")
    if test_paper > len(papers):
        log.warning("Your are trying to test more papers than available. If you want to test all papers, you can ignore this warning.")

    try:
        base_prompt = getPrompt(base_prompt_json)
    except Exception as e:
        raise ValueError(f"Error loading base prompt: {e}")

    prompt_design_prompt = PROMPT_DESIGN_PROMPT
    current_prompt = base_prompt
    papers_to_test = _get_number_of_papers(papers, 0, test_paper)
    current_accuracy = _evaluate_prompt(current_prompt, papers_to_test, csv, model, delay)

    init_log({
        "prompt_design_prompt": prompt_design_prompt,
        "base_prompt": base_prompt,
        "papers": papers,
        "tested_papers": papers_to_test,
        "base_accuracy": current_accuracy,
    })

    for i in range(loop):
        paper = _get_paper_with_index(papers, i)
        adj_prompt = adjust_prompt(current_prompt, paper, model, temp)

        papers_to_test = _get_number_of_papers(papers, i + 1, test_paper)
        accuracy = _evaluate_prompt(adj_prompt, papers_to_test, csv, model, delay)

        update_log({
            "input_prompt": current_prompt,
            "adjusted_prompt": adj_prompt,
            "paper_used_for_adjustment": paper,
            "tested_papers": papers_to_test,
            "accuracy": accuracy,
        })

        if accuracy >= current_accuracy:
            current_prompt = adj_prompt
            current_accuracy = accuracy

        if delay > 0:
            time.sleep(delay)


def _get_paper_with_index(papers: list[str], index: int) -> str:
    """Get the paper at the specified index."""
    return papers[index % len(papers)]


def _get_number_of_papers(papers: list[str], index: int, n: int) -> list[str]:
    """Gibt die nächsten n Paper ab dem gegebenen Index aus der Liste zurück (zyklisch, ohne Wiederholungen)."""
    if not papers:
        return []

    # Liste rotieren und n Elemente zurückgeben
    start = index % len(papers)
    selected = papers[start:] + papers[:start]  # zyklische Reihenfolge
    return selected[:n]

def _evaluate_prompt(prompt: str, papers_to_test: list[str], csv: str, model: str, delay: int) -> float:
    """Test the prompt using all papers and return the accuracy."""

    save_folder = None

    #run the prompt on all papers
    for paper in papers_to_test:
        same_run = True
        if save_folder is None: #makes sure to start with a new run
            same_run = False

        #TODO: add parameter for other model settings (could be generalized with a model_settings class)
        raw_answer, saved_at = process_paper(
            prompt=prompt,
            model=model,
            file_path=paper,
            same_run=same_run,
        )
        save_folder = saved_at
        if delay > 0:
            time.sleep(delay)

    #evaluate the results
    data = load_saved_jsons(save_folder + "*.json")
    compared_data = compare_data(data, csv)
    accuracy = compared_data.get('global_accuracy')

    log.info(f"Tested current Prompt; \nAccuracy: {accuracy}")
    log.info(f"Tested with the following papers: {papers_to_test}")
    if accuracy is None:
        accuracy = 0.0
        log.warning(f"⚠️  No valid comparisons for current prompt")
    return accuracy


def main():
    parser = argparse.ArgumentParser(description='Process files with specified model (e.g., gpt or gemini).')

    parser.add_argument('--model', '-m', required=False, help='Model to use (e.g., gpt-4o, gemini-3).')
    parser.add_argument('--base', '-b', required=False, help='Path to the base/default prompt.')
    parser.add_argument('--files', '-f', required=True, nargs='+', help='Files or patterns to process (supports globbing).')
    parser.add_argument('--loops', '-l', type=int, default=5, help='Number of loops to run.')
    parser.add_argument('--test_papers', type=int, default=5, help='Number of papers to test after each adjustment.')
    parser.add_argument('--delay', type=int, default=5, help='Delay time in seconds between processing files.')
    parser.add_argument('--temp', '-t', type=float, default=1.0, help='The temperature setting for model randomness.')
    parser.add_argument('--pdf_reader', action='store_true', help='Uses a local PDF reader to extract content as context for the model.')
    parser.add_argument('--csv', required=False, help='Path of the correct_answer.csv')

    args = parser.parse_args()
    model = args.model or "gemini-2.5-pro"
    base_prompt = args.base or BASIC_PROMPT_PATH
    csv = args.csv or DEFAULT_CSV

    run_prompt_designer(base_prompt, args.loops, args.test_papers, args.files, model, args.temp, csv, args.delay)

if __name__ == "__main__":
    main()
