"""
This script handles the loading and parsing of saved JSON files generated during model evaluation processes.
It supports version-based parsing and merging of answers into a unified format for further analysis.
"""

import os
import json
import glob
from evaluation import parse_csv_string_to_json
import logging

logging.basicConfig(level=logging.INFO)

def load_saved_jsons(file_pattern, combine_7abc=False):
    """
    Loads and parses multiple JSON files matching a given file pattern.
    
    Returns:
        list: A list of parsed JSON objects.
    """
    # Find all files matching the file pattern
    json_files = glob.glob(file_pattern)
    
    if not json_files:
        return []

    results = []
    for json_file in json_files:
        # Skip if not a file
        if not os.path.isfile(json_file):
            continue
        
        # Load and parse the JSON file
        result = load_json(json_file, combine_7abc)
        if result:
            results.append(result)
    
    return results

def load_json(raw_json_path, combine_7abc=False):
    """
    Loads and parses a single JSON file, handling different versions of saved data formats.
    
    Returns:
        dict or None: Parsed and normalized data dictionary if successful, otherwise None.
    """
    # Check if the file exists
    if not os.path.isfile(raw_json_path):
        return
    
    try:
        # Open and read the JSON file
        with open(raw_json_path, 'r', encoding='utf-8') as f:
            raw_data = json.load(f)
        
        # Validate required fields
        if 'Raw_Data' not in raw_data or 'PDF_Name' not in raw_data or 'Model_Name' not in raw_data:
            return
        
        version = raw_data.get('Version', 0)

        raw_answer_string = raw_data.get('Raw_Data', '-')
        pdf_name = raw_data.get('PDF_Name', '-')
        model_name = raw_data.get('Model_Name', '-')

        # Default values
        temperature = "-"
        date = "-"
        pdf_reader = "-"
        process_mode = "-"
        prompt = "-"
        pdf_reader_version = "-"
        id = "-"

        try:
            id = raw_data.get('ID', '-')
        except:
            logging.warning('Run has no ID!')

        # Parse additional fields based on version
        if version >= 1.0:
            temperature = raw_data.get('Temperature', '-')
            date = raw_data.get('Date', '-')
            pdf_reader_version = raw_data.get('PDF_Reader', '-')
            if version <= 1.0:
                if pdf_reader_version == "api-upload":
                    pdf_reader = False
                    pdf_reader_version = "-"
                else:
                    pdf_reader = True
            process_mode = raw_data.get('Process_Mode', '-')

        if version == 2.0:
            prompt = raw_data.get('Prompt', '-')
            pdf_reader_version = raw_data.get('PDF_Reader_Version', '-')
            pdf_reader = raw_data.get('PDF_Reader', '-')

        # Parse the raw answer string into structured JSON
        answers_json = parse_csv_string_to_json(raw_answer_string, combine_7abc=combine_7abc)

        data = {
            "Version": version,
            "PDF_Name": pdf_name,
            "Model_Name": model_name,
            "Prompts": answers_json,
            "Temperature": temperature,
            "Date": date,
            "PDF_Reader": pdf_reader,
            "PDF_Reader_Version": pdf_reader_version,
            "Process_Mode": process_mode,
            "Raw_Data": raw_answer_string,
            "Prompt": prompt,
            "ID": id
        }

        return data

    except Exception:
        logging.exception(f"Error while processing file {raw_json_path}")
