import argparse

from sep.env_manager import DEFAULT_CSV, BASIC_PROMPT_PATH
from sep.evaluation.load_saved_json import load_saved_jsons
from sep.prompt_designer.adjust_prompt import adjust_prompt
from sep.process_paper import process_paper
from sep.utils.load_json import load_json
from sep.prompt_designer.json_log import init_log, update_log
from sep.evaluation.compare_answers import compare_data
import random

def run_prompt_designer(base_prompt_json: str, loop: int, papers: list[str], model: str, temp: float,  csv: str):
    prompt_design_prompt = load_json(base_prompt_json)["prompt"]
    current_prompt = "base prompt"
    paper = _get_paper_with_index(papers, 0)
    current_accuracy = _evaluate_prompt(current_prompt, paper, csv)

    init_log({
        "prompt_design_prompt": prompt_design_prompt,
        "base_prompt": current_prompt,
        "papers": papers,
        "tested_papers": papers,
        "base_accuracy": current_accuracy,
    })

    for i in range(loop):
        paper = _get_paper_with_index(papers, i)
        adj_prompt = adjust_prompt(current_prompt, paper, model, temp)
        accuracy = _evaluate_prompt(adj_prompt, paper, csv)

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


def _get_random_papers(papers: list[str], n: int = 10) -> list[str]:
    """Gibt n zufällige Paper aus der Liste zurück (ohne Wiederholungen)."""
    if not papers:
        raise ValueError("Die Liste 'papers' ist leer.")
    if n > len(papers):
        n = len(papers)  # Nicht mehr als vorhanden

    return random.sample(papers, n)

def _evaluate_prompt(prompt: str, paper: str, csv: str) -> float:
    """Test the prompt using all papers and return the accuracy."""

    raw_answer, save_folder = process_paper(
        prompt=prompt,
        model="gemini-2.5-pro",
        file_path=paper,
    )

    data = load_saved_jsons(save_folder + "*.json")
    compared_data = compare_data(data, csv)
    accuracy = compared_data.get('global_accuracy')
    print(f"Prompt: {prompt}\nPaper: {paper}\nAccuracy: {accuracy}")
    if accuracy is None:
        accuracy = 0.0
        print(f"⚠️  No valid comparisons for {paper}")
    return accuracy


def main():
    parser = argparse.ArgumentParser(description='Process files with specified model (e.g., gpt or gemini).')

    parser.add_argument('--model', required=False, help='Model to use (e.g., gpt-4o, gemini-3).')
    parser.add_argument('--base', required=False, help='Path to the base/default prompt.')
    parser.add_argument('--files', required=True, nargs='+', help='Files or patterns to process (supports globbing).')
    parser.add_argument('--loops', type=int, default=5, help='Number of loops to run.')
    parser.add_argument('--delay', type=int, default=15, help='Delay time in seconds between processing files.')
    parser.add_argument('--temp', type=float, default=1.0, help='The temperature setting for model randomness.')
    parser.add_argument('--pdf_reader', action='store_true', help='Uses a local PDF reader to extract content as context for the model.')
    parser.add_argument('--csv', required=False, help='Path of the correct_answer.csv')

    args = parser.parse_args()
    model = args.model or "gemini-2.5-pro"
    base_prompt = args.base or BASIC_PROMPT_PATH
    csv = args.csv or DEFAULT_CSV

    run_prompt_designer(base_prompt, args.loops, args.files, model, args.temp, csv)

if __name__ == "__main__":
    main()
