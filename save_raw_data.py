import json
import io
import csv
import os
from datetime import datetime, timezone
import logging

logging.basicConfig(level=logging.INFO)

version_number = 2.0

def save_raw_data_as_json(raw_data, pdf_name, model_name, temp: float, pdf_reader, pdf_reader_version, process_mode, prompt):
    pdf_name = os.path.basename(pdf_name).split('.')[0]
    
    timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
    
    json_name = f"raw-{pdf_name}-{timestamp}.json"
    output_filename = "../Data/Results/" + json_name
    
    now_utc = datetime.now(timezone.utc)
    formatted_time = now_utc.strftime('%Y-%m-%dT%H:%M:%SZ')

    raw_data = {
        "Version": version_number,
        "Date": formatted_time,
        "Model_Name": model_name,
        "Temperature": temp,
        "PDF_Name": pdf_name,
        "PDF_Reader": pdf_reader,
        "PDF_Reader_Version": pdf_reader_version,
        "Process_Mode": process_mode,
        "Prompt": prompt,
        "Raw_Data": raw_data
    }

    os.makedirs(os.path.dirname(output_filename), exist_ok=True)
    
    with open(output_filename, 'w') as f:
        json.dump(raw_data, f, indent=4)

    
    logging.info(f"Saved raw data in: {output_filename}")