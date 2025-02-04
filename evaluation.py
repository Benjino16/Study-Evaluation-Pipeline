import io
import csv
import re

def parse_json_answer(answer):
    """Parse the JSON answer into '1' for yes, '0' for no, or None for invalid answers."""
    yes_answers = {"Yes", "yes"}
    no_answers = {"No", "no"}

    if answer in yes_answers:
        return '1'
    elif answer in no_answers:
        return '0'
    else:
        return None  # Invalid answer or "No Answer"

def clean_study_number(study_number):
    """Clean study number by removing file extensions and leading zeros."""
    study_number = study_number.replace('.pdf', '')  # Remove .pdf if it exists
    study_number = study_number.lstrip('0')  # Remove leading zeros
    return study_number

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

def evaluate_csv_string(csv_string, pdf_name, model_name, combine_7abc=False):
    try:
        valid_question_numbers = ['1', '2', '3', '4', '5', '6', '7a', '7b', '7c', '8', '9', '10', '11', '12']
        combine_questions = ['7a', '7b', '7c']  # Fragen, die zusammengefasst werden können
        prompts = {num: {'number': num, 'answer': 'not-existent', 'quote': 'not-existent'} for num in valid_question_numbers}

        delimiter = ";"
        csvfile = io.StringIO(csv_string)
        
        csvreader = csv.reader(csvfile, delimiter=delimiter, quotechar='"')

        question_number_pattern = re.compile(r'(\d+[a-zA-Z]?)(\.)?')

        for row in csvreader:
            if len(row) >= 3:
                raw_number = row[0].strip()
                answer = row[1].strip()
                quote = ';'.join(row[2:]).strip() if delimiter == ';' else row[2].strip()

                match = question_number_pattern.match(raw_number)
                if match:
                    number = match.group(1)

                    if number in valid_question_numbers:
                        prompts[number] = {
                            'number': number,
                            'answer': answer,
                            'quote': quote
                        }
            else:
                if len(row) == 0 or all(not cell.strip() for cell in row):
                    continue
                print(f"Warnung: Zeile hat ein falsches Format und wird ignoriert: {row}")

        if combine_7abc:
            quotes = [prompts[q]['quote'].lower() for q in combine_questions]
            answers = [prompts[q]['answer'].lower() for q in combine_questions]
            if 'no' in answers:
                combined_answer = 'no'
            elif all(ans == 'yes' for ans in answers):
                combined_answer = 'yes'
            else:
                combined_answer = 'not-existent'

            prompts['7a'] = {
                'number': '7',
                'answer': combined_answer,
                'quote': '(combined 7a, 7b, 7c): ' + ';'.join(quotes)
            }
            
            del prompts['7b']
            del prompts['7c']

        if not any(prompts.values()):
            raise ValueError("Keine gültigen Zeilen im CSV-String gefunden.")
        
    except (ValueError, Exception) as e:
        print(f"Fehler beim Verarbeiten des CSV-Strings: {e}")
        prompts = {str(i + 1): {'number': str(i + 1), 'answer': 'error', 'quote': 'error'} for i in range(3)}

    data = {
        "PDF_Name": pdf_name,
        "Model_Name": model_name,
        "Prompts": list(prompts.values())
    }

    return data
