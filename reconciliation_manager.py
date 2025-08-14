"""
Mismatch Evaluation and Reconciliation Tool

This script compares the outputs of two different model runs, identifies mismatches, 
provides an overview of model performance, and initiates a reconciliation process.
"""

import argparse
import logging
from compare_answers import run_comparison
from load_saved_json import load_saved_jsons
from evaluation import create_list
from reconciliation import reconciliate, run_reconciliation

logging.basicConfig(level=logging.INFO)

def find_entry_by_study(result_list, study_number, number):
    """
    Finds a specific entry by study number and answer number.

    Returns:
        dict or None: The found entry or None if not found.
    """
    for study in result_list:
        if study['study_number'] == study_number:
            for entry in study['answers']:
                if entry['number'] == number:
                    return entry
    return None

def evaluate_difference(run1: str, run2: str, model1: str, model2: str):
    """
    Evaluates and returns mismatches between two model runs.

    Returns:
        list: Mismatch data.
    """
    result = []
    all_mismatches = []

    data1 = load_saved_jsons(run1, False)
    data2 = load_saved_jsons(run2, False)

    if not data1 or not data2:
        raise ValueError("Both paths must contain JSON files.")

    list1 = create_list(data1)
    list2 = create_list(data2)

    for study in list1:
        study_number = study['study_number']
        mismatches = []

        for entry in study['answers']:
            number1 = entry['number']
            answer1 = entry['answer']
            quote1 = entry['quote']

            entry2 = find_entry_by_study(list2, study_number, number1)
            if entry2 is None:
                continue

            answer2 = entry2['answer']
            quote2 = entry2['quote']

            if answer1 != answer2:
                data = {
                    'number': number1,
                    'model1': {
                        'answer': answer1,
                        'quote': quote1,
                        'model': model1,
                    },
                    'model2': {
                        'answer': answer2,
                        'quote': quote2,
                        'model': model2,
                    }
                }
                mismatches.append(data)
                all_mismatches.append(data)

        if mismatches:
            result.append({
                'study_number': study_number,
                'mismatches': mismatches
            })

    return result

def reconciliation_overview(mismatches, run1: str, run2: str, model1: str, model2: str):
    """
    Prints an overview of mismatch counts and model performance.
    """
    count_mismatches = len(list_mismatches(mismatches))

    result1 = run_comparison("correct_answers.CSV", run1, False)
    result2 = run_comparison("correct_answers.CSV", run2, False)

    global_match_percentage1 = (result1['global_matches'] / result1['global_total_comparisons']) * 100
    global_match_percentage2 = (result2['global_matches'] / result2['global_total_comparisons']) * 100

    print(f"Number of mismatches: {count_mismatches}")
    print(f"{run1:<60} {run2}")
    print(f"{model1:<60} {model2}")
    print(f"{global_match_percentage1:<60.2f} {global_match_percentage2:.2f}")

def list_mismatches(mismatches):
    """
    Flattens the mismatch data into a single list.
    
    Returns:
        list: Flattened list of mismatches.
    """
    result = []
    for study in mismatches:
        for entry in study['mismatches']:
            result.append(entry)
    return result

def main():
    """
    Main entry point: Parses arguments, evaluates differences, 
    prints overview, and starts the reconciliation process.
    """
    parser = argparse.ArgumentParser(description='Compare model outputs and reconcile differences.')
    parser.add_argument('--data1', type=str, required=True, help='Path to first model run JSON data (supports globbing).')
    parser.add_argument('--data2', type=str, required=True, help='Path to second model run JSON data (supports globbing).')
    parser.add_argument('--model1', type=str, required=True, help='Name of the first model.')
    parser.add_argument('--model2', type=str, required=True, help='Name of the second model.')
    parser.add_argument('--delay', type=int, default=15, help='Delay time in seconds between processing reconciliations.')

    args = parser.parse_args()

    mismatches = evaluate_difference(args.data1, args.data2, args.model1, args.model2)
    reconciliation_overview(mismatches, args.data1, args.data2, args.model1, args.model2)
    print(mismatches)

    user_input = input("Press Enter to start the reconciliation:")
    if user_input != "":
        raise ValueError("Program aborted!")

    run_reconciliation(mismatches, args.model1, args.model2, args.delay)

if __name__ == '__main__':
    main()
