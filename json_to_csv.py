import csv
import sys
import os
from evaluate_raw import evaluate_all_raw_jsons
from compare_answers import load_correct_answers
from evaluation import parse_json_answer, clean_study_number

def json_to_csv(file_pattern, run_number, output_file=None):

    data = evaluate_all_raw_jsons(file_pattern, False)
    correct_answers = load_correct_answers("correct_answers.CSV")

    rows = []
    for entry in data:
        if 'Prompts' not in entry:
            print(f"Error: 'Prompts' key missing in one of the entries: {entry}")
            continue

        for response in entry['Prompts']:

            question_number = response.get('number', 'N/A')
            study_number = clean_study_number(entry.get('PDF_Name', 'N/A'))

            correct_answer = correct_answers[(study_number, question_number)]
            row = {
                'run': run_number,
                'pdf_name': study_number,
                'model_name': entry.get('Model_Name', 'N/A'),
                'number': question_number,
                'answer': response.get('answer', 'N/A'),
                'explanation': response.get('quote', 'N/A'),
                'answer_parsed': parse_json_answer(response.get('answer', 'N/A')),
                'correct_answer': correct_answer
            }
            rows.append(row)

    if output_file is None:
        output_file = 'output.csv'

    output_file = "../Data/CSVs/" + output_file

    file_exists = os.path.exists(output_file)

    with open(output_file, 'a' if file_exists else 'w', newline='', encoding='utf-8') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=['run', 'pdf_name', 'model_name', 'number', 'answer', 'explanation', 'answer_parsed', 'correct_answer'])
        if not file_exists:
            writer.writeheader()
        for row in rows:
            writer.writerow(row)

def main():
    if len(sys.argv) < 3:
        print("Usage: python json_to_csv.py <json_file_pattern> <run_number> <output_csv_file>")
        sys.exit(1)

    file_pattern = sys.argv[1]
    run_number = int(sys.argv[2])
    output_file = sys.argv[3]

    json_to_csv(file_pattern, run_number, output_file)

if __name__ == '__main__':
    main()
