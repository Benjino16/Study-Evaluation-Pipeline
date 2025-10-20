from sep.evaluation.load_saved_json import load_saved_jsons
from sep.evaluation.compare_answers_pandas import compare_data
from sep.env_manager import DEFAULT_CSV
import argparse
import re

def natural_sort_key(s):
    """
    Creates a key for natural sorting.
    Example: ['1', '2', '3a', '3b', '10'] -> ['1', '2', '3a', '3b', '10']
    """
    return [
        int(text) if text.isdigit() else text.lower()
        for text in re.split(r'(\d+)', str(s))
    ]

def print_result(results):
    print("\n=== accuracy per question ===")
    for q, acc in sorted(results["per_question"].items(), key=lambda x: natural_sort_key(x[0])):
        print(f"{q:<6}\t→ {acc:.3f}")

    print("\n=== accuracy per paper ===")
    for paper, acc in sorted(results["per_paper"].items(), key=lambda x: x[1], reverse=True):
        print(f"{paper:<10}\t→ {acc:.3f}")

    print("\n=== confusion matrix ===")
    print(results["confusion_matrix"])

    print("\n=== general metric ===")
    print(f"Accuracy :\t{results['overall']['accuracy']:.3f}")
    print(f"Precision:\t{results['overall']['precision']:.3f}")
    print(f"Recall   :\t{results['overall']['recall']:.3f}")
    print(f"F1-Score :\t{results['overall']['f1']:.3f}")
    print(f"Samples  :\t{results['overall']['n_samples']}")


def run_comparison(csv: str, filepath: str, combine7abc: bool, ignore_na: bool = False):
    data = load_saved_jsons(filepath, combine7abc)
    if not data:
        raise ValueError(f"No files found for pattern: {filepath}")
    return compare_data(data, csv, ignore_na)

def main():
    parser = argparse.ArgumentParser(description='Process files with specified model (gpt or gemini).')
    parser.add_argument('--data', type=str, required=True, help='The json raw data that should be evaluated (supports globbing).')
    parser.add_argument('--csv', type=str, help='The csv that the results should be compared to.')
    parser.add_argument('--combine7abc', action='store_true', help='Combines the answers of 7a, 7b and 7c to one.')
    parser.add_argument('--include_na', action='store_false', help='Ignores the NA answers, both of the model an the correct answers.')

    args = parser.parse_args()

    csv = args.csv or DEFAULT_CSV
    ignore_na = args.include_na

    data = run_comparison(csv, args.data, args.combine7abc, ignore_na)
    print_result(data)

if __name__ == '__main__':
    main()