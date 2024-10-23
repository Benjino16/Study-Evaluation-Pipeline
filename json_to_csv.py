import json
import csv
import sys
import os
import glob

def json_to_csv(json_file, run_number, output_file=None):
    with open(json_file, 'r') as f:
        data = json.load(f)

    rows = []
    for response in data['Prompts']:
        row = {
            'pdf_name': data['PDF_Name'],
            'model_name': data['Model_Name'],
            'number': response['number'],
            'answer': response['answer'],
            'explanation': response['quote'],
            'run': run_number
        }
        rows.append(row)

    if output_file is None:
        output_file = 'output.csv'

    output_file = "../Data/CSVs/" + output_file

    file_exists = os.path.exists(output_file)

    with open(output_file, 'a' if file_exists else 'w', newline='', encoding='utf-8') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=['pdf_name', 'model_name', 'number', 'answer', 'explanation', 'run'])
        if not file_exists:  # Write header only once
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

    json_files = glob.glob(file_pattern)
    
    if not json_files:
        print(f"No files found for pattern: {file_pattern}")
        sys.exit(1)

    for json_file in json_files:
        if not os.path.isfile(json_file):
            print(f"Skipping {json_file}, not a valid file.")
            continue

        print(f"Processing file: {json_file}")
        json_to_csv(json_file, run_number, output_file)

if __name__ == '__main__':
    main()
