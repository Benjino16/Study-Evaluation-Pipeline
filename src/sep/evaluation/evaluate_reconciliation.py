import glob
import json
import re
import os
import argparse
import logging

"""This script takes care of the evaluation of reconciliation runs."""

from sep.evaluation.compare_answers import compare_data, print_result, run_comparison
from sep.evaluation.load_saved_json import load_saved_jsons
from sep.evaluation.evaluation import create_list


logging.basicConfig(level=logging.INFO)

def read_reconciliation(string: str):
    """This script parses a json string gained from a comparison with an AI into a well-formatted json, which can then be further evaluated."""
    match = re.search(r'```json\s*(.*?)\s*```', string, re.DOTALL)
    if match:
        json_data = match.group(1)
        try:
            data = json.loads(json_data)
            return [mistake["number"] for mistake in data.get("mistakes", []) if "number" in mistake]
        except json.JSONDecodeError:
            pass
    return []

def evaluate_reconciliation(file_pattern: str):
    """Evaluates a reconciliation dataset retrieved from the specified file pattern."""
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
        
        except Exception:
            logging.exception(f"Error while prcessing file: {file}")
            continue
    return result

def search_in_rec(reconciliation, study_number, number) -> bool:
    """Checks whether an error has been corrected (exists) in a reconciliation data record."""
    for entry in reconciliation:
        if entry['study_number'] == study_number:
            for entry_number in entry['mistakes']:
                if str(entry_number) == number:
                    return True
    return False


def apply_reconciliation_to_data(data, reconciliation):
    """The reconciliation data set is applied to the normal data set. This means that the error correction of the AI is carried out.
    Returns the dataset with the corrected data."""
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
                logging.info(f"Corrected: {study_number} | {number}")
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

def combine_reconciliation(reconciliation, reconciliation2):
    """
    Filters out mistakes in the first reconciliation list that are present in the second reconciliation list.

    Returns:
        list of dict: A filtered list of dictionaries from the first reconciliation, with mistakes already present in the second reconciliation removed.
    """
    numbers_in_rec2 = {mistake for entry in reconciliation2 for mistake in entry['mistakes']}
    filtered_reconciliation = []
    
    for entry in reconciliation:
        filtered_mistakes = [num for num in entry['mistakes'] if num not in numbers_in_rec2]
        if filtered_mistakes:
            filtered_reconciliation.append({'study_number': entry['study_number'], 'mistakes': filtered_mistakes})
    
    return filtered_reconciliation


def main():
    parser = argparse.ArgumentParser(description='Process files with specified model (gpt or gemini).')
    parser.add_argument('--csv', type=str, required=True, help='The csv that the results should be compared to.')
    parser.add_argument('--data', type=str, required=True, help='The json raw data that should be evaluated (supports globbing).')
    parser.add_argument('--rec', type=str, required=True, help='Files or patterns to process (supports globbing).')
    parser.add_argument('--rec2', type=str, required=False, help='Add a second reconciliation run.')

    args = parser.parse_args()

    data = load_saved_jsons(args.data, False)
    list = create_list(data)

    reconciliation = evaluate_reconciliation(args.rec)
    logging.info(reconciliation)
    if args.rec2:
        reconciliation2 = evaluate_reconciliation(args.rec2)
        logging.info(reconciliation2)
        reconciliation = combine_reconciliation(reconciliation, reconciliation2)



    corrected_data = apply_reconciliation_to_data(list, reconciliation)
    logging.info(corrected_data)

    results = compare_data(corrected_data, "correct_answers.csv")
    logging.info(results)

if __name__ == '__main__':
    main()