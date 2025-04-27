import argparse
from compare_answers import run_comparrisson
from load_saved_json import load_saved_jsons
import sys
from evaluation import create_list
from reconciliation import reconciliate, run_reconciliation
            
def find_entry_by_study(result_list, study_number, number):
    for study in result_list:
        if study['study_number'] == study_number:
            for entry in study['answers']:
                if entry['number'] == number:
                    return entry
    return None

def evaluate_difference(run1: str, run2: str, model1: str, model2: str):
    result = []
    all = []

    data1 = load_saved_jsons(run1, False)
    data2 = load_saved_jsons(run2, False)

    if not data1 or not data2:
        print(f"Error: Both path must contain json files.")
        sys.exit(1)

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
                    'model1':
                    {
                        'answer': answer1,
                        'quote': quote1,
                        'model': model1,
                    },
                    'model2':
                    {
                        'answer': answer2,
                        'quote': quote2,
                        'model': model2,
                    }
                }
                mismatches.append(data)
                all.append(data)
        if len(mismatches) != 0:
            result.append({
                'study_number': study_number,
                'mismatches': mismatches
            })

    return result

def reconciliation_overview(mismatches, run1: str, run2: str, model1: str, model2: str):
    count_mismatches = len(list_mismatches(mismatches))
    
    result1 = run_comparrisson("correct_answers.CSV", run1, False)
    result2 = run_comparrisson("correct_answers.CSV", run2, False)

    global_matches1 = result1['global_matches']
    global_total_comparisons1 = result1['global_total_comparisons']
    global_match_percentage1 = (global_matches1 / global_total_comparisons1) * 100

    global_matches2 = result2['global_matches']
    global_total_comparisons2 = result2['global_total_comparisons']
    global_match_percentage2 = (global_matches2 / global_total_comparisons2) * 100

    print(f"Number of missmatches: {count_mismatches}")
    print(f"{run1:<60} {run2}")
    print(f"{model1:<60} {model2}")
    print(f"{global_match_percentage1:<60} {global_match_percentage2}")


def list_mismatches(mismatches):
    result = []
    for study in mismatches:
        study_number = study['study_number']
        data = study['mismatches']
        for entry in data:
            result.append(entry)
    return result

def main():
    parser = argparse.ArgumentParser(description='Process files with specified model (gpt or gemini).')
    parser.add_argument('--data1', type=str, required=True, help='The json raw data that should be evaluated (supports globbing).')
    parser.add_argument('--data2', type=str, required=True, help='The json raw data that should be evaluated (supports globbing).')
    parser.add_argument('--model1', type=str, required=True, help='The model that was used in first run.')
    parser.add_argument('--model2', type=str, required=True, help='The model that was used in second run.')
    parser.add_argument('--delay', type=int, default=15, help='Delay time in seconds between processing files.')

    args = parser.parse_args()

    mismatches = evaluate_difference(args.data1, args.data2, args.model1, args.model2)
    reconciliation_overview(mismatches, args.data1, args.data2, args.model1, args.model2)
    print(mismatches)
    eingabe = input("Drücke Enter, um die Reconciliation zu starten:")
    if eingabe != "":
        print("Programm wird abgebrochen.")
        exit()
    run_reconciliation(mismatches, args.model1, args.model2, args.delay)

if __name__ == '__main__':
    main()