import json
import io
import csv
import os
from datetime import datetime

def save_raw_data_as_json(csv_string, pdf_name, model_name):
    pdf_name = os.path.basename(pdf_name).split('.')[0]
    
    timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
    
    json_name = f"raw-{pdf_name}-{timestamp}.json"
    output_filename = "../Data/Results/" + json_name

    raw_data = {
        "PDF_Name": pdf_name,
        "Model_Name": model_name,
        "Raw_Data": csv_string
    }

    os.makedirs(os.path.dirname(output_filename), exist_ok=True)
    
    with open(output_filename, 'w') as f:
        json.dump(raw_data, f, indent=4)

    
    print(f"Saved raw data in: {output_filename}")
