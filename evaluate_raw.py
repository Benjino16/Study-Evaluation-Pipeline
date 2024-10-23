import sys
import os
import json
import glob
from evaluation import evaluate_csv_string

def evaluate_from_raw_json(raw_json_path, combine_7abc=False):
    if not os.path.isfile(raw_json_path):
        print(f"Fehler: Die Datei {raw_json_path} existiert nicht.")
        return
    
    try:
        with open(raw_json_path, 'r') as f:
            raw_data = json.load(f)
        
        if 'Raw_Data' not in raw_data or 'PDF_Name' not in raw_data or 'Model_Name' not in raw_data:
            print(f"Fehler: Die Datei {raw_json_path} hat nicht das erwartete Format.")
            return
        
        csv_string = raw_data['Raw_Data']
        pdf_name = raw_data['PDF_Name']
        model_name = raw_data['Model_Name']
        
        evaluate_csv_string(csv_string, pdf_name, model_name, combine_7abc=combine_7abc)
    
    except Exception as e:
        print(f"Fehler beim Verarbeiten der Datei {raw_json_path}: {e}")

def main():
    if len(sys.argv) < 2:
        print("Usage: python evaluate-raw.py /pfad/zu/json-dateien/*.json [--combine-7abc]")
        sys.exit(1)

    file_pattern = sys.argv[1]

    combine_7abc = '--combine-7abc' in sys.argv

    json_files = glob.glob(file_pattern)
    
    if not json_files:
        print(f"Keine Dateien gefunden für das Muster: {file_pattern}")
        sys.exit(1)

    for json_file in json_files:
        if not os.path.isfile(json_file):
            print(f"Überspringe {json_file}, keine gültige Datei.")
            continue

        print(f"Verarbeite Datei: {json_file}")
        evaluate_from_raw_json(json_file, combine_7abc)

if __name__ == "__main__":
    main()
