import csv
import sys
import os
import logging

"""
With the help of this script you can summarize the answers of 7a, 7b and 7c in a CSVs and JSONs.
"""

logging.basicConfig(level=logging.INFO)

def combine_7abc(study_rows):
    """
    With the help of this script you can combine the answers from 7a, 7b and 7c into a CSV and create a new CSV from it.
    If all answers are '1', '1' is returned, if at least one is '0', '0' is returned.
    NA' is ignored if there are other valid answers.  
    """
    answers = {'7a': 'NA', '7b': 'NA', '7c': 'NA'}

    # Extract answers for 7a, 7b, 7c from the rows
    for row in study_rows:
        if row['prompt_number'] in answers:
            answers[row['prompt_number']] = row['answer']
    
    valid_answers = [ans for ans in answers.values() if ans != 'NA']
    
    if not valid_answers:
        return 'NA'
    
    if all(ans == '1' for ans in valid_answers):
        return '1'
    
    if any(ans == '0' for ans in valid_answers):
        return '0'
    
    return 'NA'

def process_csv(input_csv, output_csv):
    """Reads the CSV file, combines 7a, 7b and 7c and writes them to a new CSV file."""

    with open(input_csv, newline='') as csvfile:
        reader = csv.DictReader(csvfile, delimiter=';')
        fieldnames = reader.fieldnames
        
        # create new csv file
        with open(output_csv, 'w', newline='') as new_csvfile:
            writer = csv.DictWriter(new_csvfile, fieldnames=fieldnames, delimiter=';')
            writer.writeheader()

            current_study = None
            study_rows = []

            # loop through each row
            for row in reader:
                study_number = row['study_number']
                prompt_number = row['prompt_number']
                
                # processes the previous study, once the current one changes
                if study_number != current_study:
                    if current_study is not None:
                        process_study(writer, study_rows)

                    current_study = study_number
                    study_rows = [row]
                else:
                    study_rows.append(row)

            if study_rows:
                process_study(writer, study_rows)

def process_study(writer, study_rows):
    """Processes a single study, summarizes 7a, 7b, 7c to 7 and writes the result."""

    new_rows = []
    found_7abc = False
    
    # Go through all lines of the study and keep lines except 7a, 7b, 7c
    for row in study_rows:
        prompt_number = row['prompt_number']
        
        if prompt_number in ['7a', '7b', '7c']:
            found_7abc = True
        else:
            new_rows.append(row)
    
    # If 7a, 7b, 7c were present, combine them into a new line for 7
    if found_7abc:
        combined_answer = combine_7abc(study_rows)
        new_rows.append({
            'study_number': study_rows[0]['study_number'],
            'prompt_number': '7',
            'answer': combined_answer
        })

    # Write the new lines to the output
    for new_row in new_rows:
        writer.writerow(new_row)

def main():
    if len(sys.argv) != 3:
        raise ValueError("Usage: python combine_7abc.py <input_csv_file> <output_csv_file>")

    input_csv = sys.argv[1]
    output_csv = sys.argv[2]

    if not os.path.isfile(input_csv):
        raise ValueError(f"File {input_csv} not found.")

    # Process CSV and combine 7a, 7b, 7c
    process_csv(input_csv, output_csv)
    logging.info(f"CSV-Prozess completed. File was created as: {output_csv}")

if __name__ == '__main__':
    main()
