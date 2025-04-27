import csv
import sys
import os
import logging

logging.basicConfig(level=logging.INFO)

def combine_7abc(study_rows):
    """
    Kombiniert die Antworten für 7a, 7b, und 7c zu einer Antwort für 7.
    Wenn alle Antworten '1' sind, wird '1' zurückgegeben, bei mindestens einer '0' wird '0' zurückgegeben.
    'NA' wird ignoriert, wenn es andere gültige Antworten gibt.
    """
    answers = {'7a': 'NA', '7b': 'NA', '7c': 'NA'}

    # Antworten für 7a, 7b, 7c aus den rows extrahieren
    for row in study_rows:
        if row['prompt_number'] in answers:
            answers[row['prompt_number']] = row['answer']
    
    valid_answers = [ans for ans in answers.values() if ans != 'NA']
    
    if not valid_answers:
        return 'NA'
    
    if all(ans == '1' for ans in valid_answers):
        return '1'
    
    if any(ans == '0' for ans in valid_answers):
        return '0'
    
    return 'NA'

def process_csv(input_csv, output_csv):
    """Liest die CSV-Datei, fasst 7a, 7b und 7c zusammen und schreibt sie in eine neue CSV-Datei."""
    with open(input_csv, newline='') as csvfile:
        reader = csv.DictReader(csvfile, delimiter=';')
        fieldnames = reader.fieldnames
        
        # Neue CSV-Datei erstellen
        with open(output_csv, 'w', newline='') as new_csvfile:
            writer = csv.DictWriter(new_csvfile, fieldnames=fieldnames, delimiter=';')
            writer.writeheader()

            current_study = None
            study_rows = []

            # Zeilenweise durch das Original gehen
            for row in reader:
                study_number = row['study_number']
                prompt_number = row['prompt_number']
                
                # Wenn wir zu einer neuen Studie wechseln, verarbeite die vorherige Studie
                if study_number != current_study:
                    if current_study is not None:
                        # Verarbeite die Zeilen der aktuellen Studie
                        process_study(writer, study_rows)

                    # Neue Studie beginnen
                    current_study = study_number
                    study_rows = [row]
                else:
                    study_rows.append(row)

            # Verarbeite die letzte Studie
            if study_rows:
                process_study(writer, study_rows)

def process_study(writer, study_rows):
    """Verarbeitet eine einzelne Studie, fasst 7a, 7b, 7c zu 7 zusammen und schreibt das Ergebnis."""
    new_rows = []
    found_7abc = False
    
    # Gehe alle Zeilen der Studie durch und behalte Zeilen außer 7a, 7b, 7c bei
    for row in study_rows:
        prompt_number = row['prompt_number']
        
        if prompt_number in ['7a', '7b', '7c']:
            found_7abc = True
        else:
            new_rows.append(row)
    
    # Wenn 7a, 7b, 7c vorhanden waren, kombiniere sie zu einer neuen Zeile für 7
    if found_7abc:
        combined_answer = combine_7abc(study_rows)
        new_rows.append({
            'study_number': study_rows[0]['study_number'],
            'prompt_number': '7',
            'answer': combined_answer
        })

    # Schreibe die neuen Zeilen in die Ausgabe
    for new_row in new_rows:
        writer.writerow(new_row)

def main():
    if len(sys.argv) != 3:
        logging.error("Usage: python combine_7abc.py <input_csv_file> <output_csv_file>")
        sys.exit(1)

    input_csv = sys.argv[1]
    output_csv = sys.argv[2]

    if not os.path.isfile(input_csv):
        logging.error(f"File {input_csv} not found.")
        sys.exit(1)

    # CSV verarbeiten und 7a, 7b, 7c kombinieren
    process_csv(input_csv, output_csv)
    logging.info(f"CSV-Prozess completed. File was created as: {output_csv}")

if __name__ == '__main__':
    main()
