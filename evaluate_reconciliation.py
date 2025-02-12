import glob
import json
import re
import os
import argparse

from compare_answers import compare_data, print_result, run_comparrisson
from evaluate_raw import evaluate_all_raw_jsons
from evaluation import create_list

def read_reconciliation(string: str):
    match = re.search(r'```json\s*(.*?)\s*```', string, re.DOTALL)
    if match:
        json_data = match.group(1)
        try:
            data = json.loads(json_data)
            return data.get("mistakes", [])
        except json.JSONDecodeError:
            pass
    return []

def evaluate_reconciliation(file_pattern: str):
    result = []
    files_to_process = []
    files_to_process.extend(glob.glob(file_pattern))

    for file in files_to_process:
        if not os.path.isfile(file):
            return
        
        try:
            with open(file, 'r') as f:
                raw_data = json.load(f)
            
            if 'Raw_Data' not in raw_data or 'PDF_Name' not in raw_data or 'Model_Name' not in raw_data:
                return
            
            data_string = raw_data['Raw_Data']
            pdf_name = raw_data['PDF_Name']
            model_name = raw_data['Model_Name']
            
            number_list = read_reconciliation(data_string)
            if len(number_list) > 0:
                result.append({
                    'study_number': pdf_name,
                    'mistakes': number_list
                })
        
        except Exception as e:
            print(f"Fehler beim Verarbeiten der Datei {file}: {e}")
    return result

def search_in_rec(reconciliation, study_number, number) -> bool:
    for entry in reconciliation:
        if entry['study_number'] == study_number:
            for entry_number in entry['mistakes']:
                if str(entry_number) == number:
                    return True
    return False


def apply_reconciliation_to_data(data, reconciliation):
    corrected_data = []
    for study in data:
        study_number = study['study_number']
        answers = []

        for entry in study['answers']:
            number = entry['number']
            answer = entry['answer']
            quote = entry['quote']

            correct = search_in_rec(reconciliation, study_number, number)
            if correct and answer != None:
                print(f"Corrected: {study_number} | {number}")
                answer = 1 - int(answer)

            answers.append({
                'number': number,
                'answer': answer,
                'quote': quote
            })

        corrected_data.append({
                'PDF_Name': study_number,
                'Prompts': answers
            })
    return corrected_data

def main():
    parser = argparse.ArgumentParser(description='Process files with specified model (gpt or gemini).')
    parser.add_argument('--csv', type=str, required=True, help='The csv that the results should be compared to.')
    parser.add_argument('--data', type=str, required=True, help='The json raw data that should be evaluated (supports globbing).')
    parser.add_argument('--rec', type=str, required=True, help='Files or patterns to process (supports globbing).')
    parser.add_argument('--combine7abc', action='store_true', help='Combines the answers of 7a, 7b and 7c to one.')

    args = parser.parse_args()
    
    data = evaluate_all_raw_jsons(args.data, False)
    list = create_list(data)

    reconciliation = evaluate_reconciliation(args.rec)
    print(reconciliation)
    corrected_data = apply_reconciliation_to_data(list, reconciliation)
    print(corrected_data)

    results = compare_data(corrected_data, "correct_answers.csv")
    print_result(results)



if __name__ == '__main__':
    main()