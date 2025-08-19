"""
Module to save raw model outputs as structured JSON files.
It captures metadata like model name, temperature, processing mode, and timestamps.
"""

import json
import io
import csv
import os
from datetime import datetime, timezone
import logging
from .env_manager import RESULT_FOLDER

logging.basicConfig(level=logging.INFO)

version_number = 2.0

def save_raw_data_as_json(raw_data, pdf_name, model_name, temp: float, pdf_reader, pdf_reader_version, process_mode, prompt):
    """
    Saves raw output data along with metadata into a JSON file.
    """

    # Prepare the base PDF name (without extension)
    pdf_name = os.path.basename(pdf_name).split('.')[0]

    # Generate a timestamp for the filename
    timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")

    # Set output filename
    json_name = f"raw-{pdf_name}-{timestamp}.json"
    output_filename = RESULT_FOLDER + json_name

    # Create UTC timestamp
    now_utc = datetime.now(timezone.utc)
    formatted_time = now_utc.strftime('%Y-%m-%dT%H:%M:%SZ')

    # Structure the output data
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

    # Ensure output directory exists
    os.makedirs(os.path.dirname(output_filename), exist_ok=True)

    # Write data to JSON file
    with open(output_filename, 'w') as f:
        json.dump(raw_data, f, indent=4)

    logging.info(f"Saved raw data in: {output_filename}")
