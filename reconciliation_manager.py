import argparse
from compare_answers import run_comparrisson
from evaluate_raw import evaluate_all_raw_jsons
import sys
from evaluation import create_list
from reconciliation import reconciliate
            
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

    data1 = evaluate_all_raw_jsons(run1, False)
    data2 = evaluate_all_raw_jsons(run2, False)

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

    result1 = run_comparrisson("correct_answers.CSV", run1, False)
    global_matches = result1['global_matches']
    global_total_comparisons = result1['global_total_comparisons']
    global_match_percentage1 = (global_matches / global_total_comparisons) * 100
    print(f"Number of missmatches: {len(all)}")
    print(f"Acc1: {global_match_percentage1}")
    
    return result

def run_reconciliation(mismatches, model1: str, model2: str):
    for study in mismatches:
        study_number = study['study_number']
        data = study['mismatches']
        reconciliate(data, study_number, model1, model2)


def main():
    parser = argparse.ArgumentParser(description='Process files with specified model (gpt or gemini).')
    parser.add_argument('--data1', type=str, required=True, help='The json raw data that should be evaluated (supports globbing).')
    parser.add_argument('--data2', type=str, required=True, help='The json raw data that should be evaluated (supports globbing).')
    parser.add_argument('--model1', type=str, required=True, help='The model that was used in first run.')
    parser.add_argument('--model2', type=str, required=True, help='The model that was used in second run.')
    args = parser.parse_args()

    mismatches = evaluate_difference(args.data1, args.data2, args.model1, args.model2)
    run_reconciliation(mismatches, args.model1, args.model2)

if __name__ == '__main__':
    main()