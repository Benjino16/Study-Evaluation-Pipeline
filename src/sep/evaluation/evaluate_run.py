from sep.evaluation.load_saved_json import load_saved_jsons
from sep.evaluation.compare_answers import compare_data
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

def colorize_accuracy(acc):
    """
    Dynamische Farbgebung:
    Rot (≤0.5) → Gelb (~0.6) → Grün (~0.75) → Blau (≥0.85)
    Funktioniert in Terminals mit TrueColor-Unterstützung (ANSI 24-bit).
    """
    # acc clampen (nur 0–1 zulassen)
    acc = max(0.0, min(1.0, acc))

    if acc < 0.6:
        # Rot → Gelb
        ratio = acc / 0.6
        r = 255
        g = int(255 * ratio)
        b = 0
    elif acc < 0.75:
        # Gelb → Grün
        ratio = (acc - 0.6) / (0.75 - 0.6)
        r = int(255 * (1 - ratio))
        g = 255
        b = 0
    elif acc < 0.85:
        # Grün → Türkis
        ratio = (acc - 0.75) / (0.85 - 0.75)
        r = 0
        g = 255
        b = int(255 * ratio)
    else:
        # Türkis → Blau
        ratio = (acc - 0.85) / (1.0 - 0.85)
        r = 0
        g = int(255 * (1 - ratio))
        b = 255

    color = f"\033[38;2;{r};{g};{b}m"
    reset = "\033[0m"
    return f"{color}{acc:.3f}{reset}"




def print_result(results):
    print("\n=== accuracy per question ===")
    for q, acc in sorted(results["per_question"].items(), key=lambda x: natural_sort_key(x[0])):
        print(f"{q:<6}\t→ {colorize_accuracy(acc)}")

    print("\n=== accuracy per paper ===")
    for paper, acc in sorted(results["per_paper"].items(), key=lambda x: x[1], reverse=True):
        print(f"{paper:<10}\t→ {colorize_accuracy(acc)}")

    print("\n=== confusion matrix ===")
    print(results["confusion_matrix"])

    print("\n=== overall metric ===")
    overall = results["overall"]
    print(f"Accuracy :\t{colorize_accuracy(overall['accuracy'])}")
    print(f"Precision:\t{colorize_accuracy(overall['precision'])}")
    print(f"Recall   :\t{colorize_accuracy(overall['recall'])}")
    print(f"F1-Score :\t{colorize_accuracy(overall['f1'])}")
    print(f"Samples  :\t{overall['n_samples']}")



def run_comparison(csv: str, filepath: str, combine7abc: bool):
    data = load_saved_jsons(filepath, combine7abc)
    if not data:
        raise ValueError(f"No files found for pattern: {filepath}")
    return compare_data(data, csv, combine7abc)

def main():
    parser = argparse.ArgumentParser(description='Process files with specified model (gpt or gemini).')
    parser.add_argument('--data', type=str, required=True, help='The json raw data that should be evaluated (supports globbing).')
    parser.add_argument('--csv', type=str, help='The csv that the results should be compared to.')
    parser.add_argument('--combine7abc', '-7', action='store_true', help='Combines the answers of 7a, 7b and 7c to one.')

    args = parser.parse_args()
    csv = args.csv or DEFAULT_CSV
    data = run_comparison(csv, args.data, args.combine7abc)
    print_result(data)

if __name__ == '__main__':
    main()