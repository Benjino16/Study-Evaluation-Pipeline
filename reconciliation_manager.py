import argparse
from compare_answers import run_comparrisson
from evaluate_raw import evaluate_all_raw_jsons
import sys
from evaluation import create_list
            
def find_entry_by_study_and_number(result_list, study_number, number):
    for entry in result_list:
        if entry['study_number'] == study_number and entry['number'] == number:
            return entry  # Eintrag gefunden
    return None  # Kein Eintrag gefunden

def run_reconciliation(run1: str, run2: str):
    mismatches = []

    data1 = evaluate_all_raw_jsons(run1, False)
    data2 = evaluate_all_raw_jsons(run2, False)

    if not data1 or not data2:
        print(f"Error: Both path must contain json files.")
        sys.exit(1)

    list1 = create_list(data1)
    list2 = create_list(data2)

    for entry1 in list1:
        study_number1 = entry1['study_number']
        number1 = entry1['number']
        answer1 = entry1['answer']
        quote1 = entry1['quote']

        entry2 = find_entry_by_study_and_number(list2, study_number1, number1)
        if entry2 is None:
            continue

        answer2 = entry2['answer']
        quote2 = entry2['quote']

        if answer1 != answer2:
            mismatches.append([
                {
                    'answer': answer1,
                    'quote': quote1,
                    'model': "test",
                },
                {
                    'answer': answer2,
                    'quote': quote2,
                    'model': "test",
                }
            ])
    result1 = run_comparrisson("correct_answers.CSV", run1, False)
    global_matches = result1['global_matches']
    global_total_comparisons = result1['global_total_comparisons']
    global_match_percentage1 = (global_matches / global_total_comparisons) * 100
    print(f"Number of missmatches: {len(mismatches)}")
    print(f"Acc1: {global_match_percentage1}")

def main():
    parser = argparse.ArgumentParser(description='Process files with specified model (gpt or gemini).')
    parser.add_argument('--data1', type=str, required=True, help='The json raw data that should be evaluated (supports globbing).')
    parser.add_argument('--data2', type=str, required=True, help='The json raw data that should be evaluated (supports globbing).')
    args = parser.parse_args()

    run_reconciliation(args.data1, args.data2)

if __name__ == '__main__':
    main()