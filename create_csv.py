import argparse
import csv
import sys
import os
import env_manager
from load_saved_json import load_saved_jsons
from compare_answers import load_correct_answers, load_human_answers
from evaluation import parse_json_answer, clean_study_number
import logging

logging.basicConfig(level=logging.INFO)

def create_csv(file_pattern, run_id, correct_answers, output_file=None, validation: bool=False):
    """Creates a CSV file from a run, which contains all useful information of the run in long format.
    If there is already a file with the name, the content is appended."""

    data = load_saved_jsons(file_pattern, False)
    correct_answers = load_correct_answers(correct_answers)
    human_answers = load_human_answers("human_reviewer_answers.csv")

    rows = []
    for entry in data:
        if 'Prompts' not in entry:
            logging.warning(f"'Prompts' key missing in one of the entries: {entry}")
            continue

        for response in entry['Prompts']:

            question_number = response.get('number', 'N/A')
            study_number = clean_study_number(entry.get('PDF_Name', 'N/A'))

            try:
                correct_answer = correct_answers[(study_number, question_number)]
            except:
                correct_answer = "not in dataset"

            try:
                human1, human2 = human_answers[(study_number, question_number)]
            except:
                human1, human2 = "not in dataset", "not in dataset"
            

            row = {
                #general information of the run
                'run': run_id,
                'model_name': entry.get('Model_Name', 'N/A'),
                'temp': entry.get('Temperature', 'N/A'),
                "pdf_reader": entry.get('PDF_Reader', 'N/A'),
                "pdf_reader_version": entry.get('PDF_Reader_Version', 'N/A'),
                "process_mode": entry.get('Process_Mode', 'N/A'),
                "validation": validation,

                #information related to specific study
                'pdf_name': study_number,
                "date": entry.get('Date', 'N/A'),
                "raw_answer": entry.get('Raw_Data', 'N/A'),

                #information related to a specific question
                'number': question_number,
                'answer': response.get('answer', 'N/A'),
                'explanation': response.get('quote', 'N/A'),
                
                
                'answer_parsed': parse_json_answer(response.get('answer', 'N/A')),
                'correct_answer': correct_answer,
                'human1': human1,
                'human2': human2
            }
            rows.append(row)

    if output_file is None:
        output_file = 'output.csv'

    output_file = env_manager.CSV_FOLDER + output_file

    file_exists = os.path.exists(output_file)

    with open(output_file, 'a' if file_exists else 'w', newline='', encoding='utf-8') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=[
            'run',
            'model_name',
            'temp',
            'pdf_reader',
            'pdf_reader_version',
            'process_mode',
            'validation',
            'pdf_name',
            'date',
            'raw_answer',
            'number',
            'answer',
            'explanation',
            'answer_parsed',
            'correct_answer',
            'human1',
            'human2'
        ])
        if not file_exists:
            writer.writeheader()
        for row in rows:
            writer.writerow(row)
    logging.info("Created csv for " + file_pattern)

def loop_runs(dir, csv_name, correct_answers, number):
    """loops through several runs and creates a CSV from them."""
    
    if not os.path.isdir(dir):
            logging.error(f"The directory {dir} does not exist.")
            return
    
    folder_list = [f for f in os.listdir(dir) if os.path.isdir(os.path.join(dir, f)) and not f.startswith(".")]

    if not folder_list:
        logging.error(f"There are no valid sub folders in {dir}.")
        return
    
    for i, folder in enumerate(folder_list, start=number):
        folder_path = os.path.join(dir, folder) + "/*.json"
        create_csv(folder_path, i, correct_answers, csv_name)
        logging.info(f"Last number: {i}")


def main():
    parser = argparse.ArgumentParser(description='Creates a csv from either a specific run or a run directory.')
    parser.add_argument('--run', required=False, help='A specific run from which the csv should be created')
    parser.add_argument('--dir', required=False, help='A run folder from where the csv is created with all runs.')
    parser.add_argument('--name', required=True, help='A name of the csv.')
    parser.add_argument('--csv', required=True, help='Path of the correct_asnwer.csv')
    parser.add_argument('--validation', action='store_true', help='Marks the run as a validation run.')
    parser.add_argument('--number', type=int, required=True, help='The run ID')
    args = parser.parse_args()

    

    if args.run:
        create_csv(args.run, args.number, args.csv, args.name, args.validation)
    else:
        if args.dir:
            loop_runs(args.dir, args.name, args.csv, args.number)
        else:
            raise ValueError(f"Either a dir or a run must be provided!")
    

if __name__ == '__main__':
    main()
