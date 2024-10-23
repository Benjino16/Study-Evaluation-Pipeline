import csv
import sys
import os
from evaluate_raw import evaluate_all_raw_jsons

def json_to_csv(data, run_number, output_file=None):
    rows = []
    for entry in data:
        if 'Prompts' not in entry:
            print(f"Error: 'Prompts' key missing in one of the entries: {entry}")
            continue

        for response in entry['Prompts']:
            row = {
                'pdf_name': entry.get('PDF_Name', 'N/A'),
                'model_name': entry.get('Model_Name', 'N/A'),
                'number': response.get('number', 'N/A'),
                'answer': response.get('answer', 'N/A'),
                'explanation': response.get('quote', 'N/A'),
                'run': run_number
            }
            rows.append(row)

    if output_file is None:
        output_file = 'output.csv'

    output_file = "../Data/CSVs/" + output_file

    file_exists = os.path.exists(output_file)

    with open(output_file, 'a' if file_exists else 'w', newline='', encoding='utf-8') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=['pdf_name', 'model_name', 'number', 'answer', 'explanation', 'run'])
        if not file_exists:
            writer.writeheader()
        for row in rows:
            writer.writerow(row)

def main():
    if len(sys.argv) < 3 or len(sys.argv) > 4:
        print("Usage: python json_to_csv.py <json_file_pattern> <run_number> [<output_csv_file>]")
        sys.exit(1)

    file_pattern = sys.argv[1]
    run_number = int(sys.argv[2])
    output_file = sys.argv[3] if len(sys.argv) == 4 else None

    data = evaluate_all_raw_jsons(file_pattern, False)
    json_to_csv(data, run_number, output_file)

if __name__ == '__main__':
    main()
