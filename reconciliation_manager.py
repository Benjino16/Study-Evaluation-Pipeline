import argparse
from evaluate_raw import evaluate_all_raw_jsons
from compare_answers import clean_study_number
from compare_answers import parse_json_answer
import sys
    
def create_list(data):
    result_list = []

    for entry in data:
        study_number = clean_study_number(entry['PDF_Name'])
        for response in entry['Prompts']:
            number = response['number']
            answer = parse_json_answer(response['answer'])
            quote = response['quote']

            result_list.append({
                'study_number': study_number,
                'number': number,
                'answer': answer,
                'quote': quote
            })
    return result_list

            
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

    print(mismatches)

def main():
    parser = argparse.ArgumentParser(description='Process files with specified model (gpt or gemini).')
    parser.add_argument('--data1', type=str, required=True, help='The json raw data that should be evaluated (supports globbing).')
    parser.add_argument('--data2', type=str, required=True, help='The json raw data that should be evaluated (supports globbing).')
    args = parser.parse_args()

    run_reconciliation(args.data1, args.data2)

if __name__ == '__main__':
    main()