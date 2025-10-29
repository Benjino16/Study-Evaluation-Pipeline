import os
import csv
import json
from typing import Union, Dict

def get_correct_answers(
    paper: str,
    csv_path: str = r"D:\dev\github\Study-Evaluation-Pipeline\resources\csv\correct_answers.CSV"
) -> Union[str, Dict[str, str]]:
    """
    Gibt die korrekten Antworten für das angegebene Paper zurück.
    Erwartet CSV mit Format: paper_id;question_id;answer
    Konvertiert 1→'yes', 0→'no', NA bleibt erhalten.
    """
    # --- 1. Existenz prüfen ---
    if not os.path.exists(csv_path):
        return f"❌ Fehler: CSV-Datei wurde nicht gefunden unter '{csv_path}'."

    # --- 2. Papernummer extrahieren ---
    try:
        paper_num_str = os.path.splitext(os.path.basename(paper))[0]
        paper_num = int(paper_num_str.lstrip("0") or "0")
    except ValueError:
        return f"❌ Fehler: Konnte keine gültige Paper-Nummer aus '{paper}' extrahieren."

    # --- 3. CSV einlesen ---
    try:
        with open(csv_path, mode="r", encoding="utf-8-sig", newline="") as f:
            # Versuch, das Trennzeichen automatisch zu erkennen
            sample = f.read(2048)
            f.seek(0)
            try:
                dialect = csv.Sniffer().sniff(sample, delimiters=";,")
            except csv.Error:
                dialect = csv.get_dialect("excel")
                dialect.delimiter = ";"
            reader = csv.reader(f, dialect)
            data = [[cell.strip() for cell in row] for row in reader if any(row)]
    except Exception as e:
        return f"❌ Fehler beim Einlesen der CSV-Datei: {e}"

    if not data:
        return f"⚠️ CSV-Datei '{os.path.basename(csv_path)}' ist leer."

    # --- 4. Header entfernen ---
    if data and any("paper" in c.lower() for c in data[0]):
        data = data[1:]

    # --- 5. Antworten extrahieren ---
    answers = {}
    for row in data:
        if len(row) < 3:
            continue
        raw_paper_id, question_id, answer = row[:3]
        try:
            paper_id = int(str(raw_paper_id).lstrip("0") or "0")
        except ValueError:
            continue
        if paper_id == paper_num:
            # Konvertiere numerische Werte
            normalized = answer.strip().upper()
            if normalized == "1":
                converted = "yes"
            elif normalized == "0":
                converted = "no"
            else:
                converted = answer  # z. B. "NA"
            answers[question_id] = converted

    # --- 6. Prüfen, ob etwas gefunden wurde ---
    if not answers:
        found_ids = sorted({r[0] for r in data if r and r[0].strip()})
        return f"⚠️ Keine Antworten für Paper {paper_num} gefunden. In CSV erkannt: {found_ids}"

    return json.dumps(answers)

