import os
import argparse
import json
import glob
import re
from datetime import datetime

DATE_PATTERN = re.compile(r"raw-(\d{4})-(\d{8})-(\d{6})\.json")

def parse_filename(filename):
    """Extrahiert PDF_Name und Date aus dem Dateinamen."""
    basename = os.path.basename(filename)
    match = DATE_PATTERN.match(basename)
    if not match:
        raise ValueError(f"Ungültiges Dateiformat: {basename}")
    
    pdf_number, date_str, time_str = match.groups()
    date_iso = datetime.strptime(date_str + time_str, "%Y%m%d%H%M%S").isoformat() + "Z"
    return pdf_number, date_iso

def process_file(file_path, process_mode, temperature, pdf_reader):
    with open(file_path, "r", encoding="utf-8") as f:
        old_data = json.load(f)

    pdf_number, date_iso = parse_filename(file_path)

    new_data = {
        "PDF_Name": old_data.get("PDF_Name", pdf_number),
        "Model_Name": old_data["Model_Name"],
        "Raw_Data": old_data["Raw_Data"],
        "Version": 1,
        "Date": date_iso,
        "Temperature": temperature,
        "PDF_Reader": pdf_reader,
        "Process_Mode": process_mode
    }

    # Optional: Überschreibe oder speichere unter neuem Namen
    with open(file_path, "w", encoding="utf-8") as f:
        json.dump(new_data, f, indent=4)
    print(f"Verarbeitet: {file_path}")

def main():
    parser = argparse.ArgumentParser(description="Konvertiere alte JSON-Dateien ins neue Format.")
    parser.add_argument("--glob", required=True, help="Glob-Pfad zu den JSON-Dateien, z.B. 'data/*.json'")
    parser.add_argument("--process_mode", required=True, help="Wert für Process_Mode")
    parser.add_argument("--temperature", type=float, required=True, help="Wert für Temperature (z.B. 0.2)")
    parser.add_argument("--pdf_reader", required=True, help="Wert für PDF_Reader (z.B. 'api-upload')")

    args = parser.parse_args()

    files = glob.glob(args.glob)
    if not files:
        print("Keine passenden Dateien gefunden.")
        return

    for file_path in files:
        try:
            process_file(file_path, args.process_mode, args.temperature, args.pdf_reader)
        except Exception as e:
            print(f"Fehler bei {file_path}: {e}")

if __name__ == "__main__":
    main()
