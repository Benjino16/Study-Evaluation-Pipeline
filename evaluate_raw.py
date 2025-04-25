import os
import json
import glob
from evaluation import parse_csv_string_to_json

def evaluate_from_raw_json(raw_json_path, combine_7abc=False):
    if not os.path.isfile(raw_json_path):
        return
    
    try:
        with open(raw_json_path, 'r') as f:
            raw_data = json.load(f)
        
        if 'Raw_Data' not in raw_data or 'PDF_Name' not in raw_data or 'Model_Name' not in raw_data:
            return
        
        raw_answer_string = raw_data['Raw_Data']
        pdf_name = raw_data['PDF_Name']
        model_name = raw_data['Model_Name']

        temperature = raw_data['Temperature']
        date = raw_data['Date']
        pdf_reader = raw_data['PDF_Reader']
        pdf_reader_version = raw_data['PDF_Reader_Version']
        process_mode = raw_data['Process_Mode']
        prompt = raw_data['Prompt']
        
        answers_json = parse_csv_string_to_json(raw_answer_string, combine_7abc=combine_7abc)

        data = {
            "PDF_Name": pdf_name,
            "Model_Name": model_name,
            "Prompts": answers_json,
            "Temperature": temperature,
            "Date": date,
            "PDF_Reader": pdf_reader,
            "PDF_Reader_Version": pdf_reader_version,
            "Process_Mode": process_mode,
            "Raw_Data": raw_answer_string,
            "Prompt": prompt
        }
        
        return data
    
    except Exception as e:
        print(f"Fehler beim Verarbeiten der Datei {raw_json_path}: {e}")

def evaluate_all_raw_jsons(file_pattern, combine_7abc=False):
    json_files = glob.glob(file_pattern)
    
    if not json_files:
        return []

    results = []
    for json_file in json_files:
        if not os.path.isfile(json_file):
            continue

        result = evaluate_from_raw_json(json_file, combine_7abc)
        if result:
            results.append(result)
    
    return results