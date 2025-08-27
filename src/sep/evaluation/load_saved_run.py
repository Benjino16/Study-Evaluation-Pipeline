"""
This script handles the loading and parsing of saved JSON files generated during model evaluation processes.
It supports version-based parsing and merging of answers into a unified format for further analysis.
"""

import os
import json
import glob
from sep.utils.parse_csv_answers import parse_csv_string_to_json
import logging

from sep.models.llm_runs.run import LLMRun, LLMRequest
from sep.models.llm_runs.evaluation import LLMEvaluatedQuestion

logging.basicConfig(level=logging.INFO)

def load_saved_jsons(file_pattern, combine_7abc=False) -> LLMRun:
    """
    Loads and parses multiple JSON files matching a given file pattern.
    
    Returns:
        list: A list of parsed JSON objects.
    """

    llmRun = LLMRun(requests=[])

    # Find all files matching the file pattern
    json_files = glob.glob(file_pattern)
    
    if not json_files:
        return []

    results = []

    run_data_set=False
    for json_file, i in json_files:
        # Skip if not a file
        if not os.path.isfile(json_file):
            continue
        # Load and parse the JSON file
        llmrequest = load_llm_request_from_json(json_file, combine_7abc)
        if llmrequest:
            llmRun.add_request(llmrequest)
            if not run_data_set:
                llmRun.id = llmrequest.run_id
                llmRun.model = llmrequest.model
                llmRun.date = llmrequest.date
                llmRun.pdf_reader = llmrequest.pdf_reader
                llmRun.pdf_reader_version = llmrequest.pdf_reader
                llmRun.process_mode = llmrequest.process_mode
                llmRun.raw_input = llmrequest.raw_input
                llmRun.temperature = llmrequest.temperature

                run_data_set=True
    
    return llmRun

def load_llm_request_from_json(raw_json_path, combine_7abc=False) -> LLMRequest:
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

        llmRequest = LLMRequest(
            version=version,
            paper=pdf_name,
            model=model_name,
            temperature=temperature,
            date=date,
            pdf_reader=pdf_reader,
            pdf_reader_version=pdf_reader_version,
            process_mode=process_mode,
            raw_input=prompt,
            id=id,
            raw_output=raw_answer_string,
            run_id=id
            answers=[LLMEvaluatedQuestion(id=ans['number'], answer=ans['answer'], quote=ans['quote']) for ans in answers_json]
            )

        return llmRequest

    except Exception:
        logging.exception(f"Error while processing file {raw_json_path}")
