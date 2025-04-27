import os
import platform
import argparse
import json
from tabulate import tabulate
from compare_answers import run_comparrisson, print_result

def clear_console():
    if platform.system() == "Windows":
        os.system("cls")
    else:
        os.system("clear")

def read_json_from_folder(folder_path):
    """Liest die erste nicht versteckte JSON-Datei in einem Ordner und gibt die relevanten Daten zurück."""
    for file in os.listdir(folder_path):
        if file.endswith(".json") and not file.startswith("."):
            file_path = os.path.join(folder_path, file)
            try:
                with open(file_path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                return {
                    "Model Name": data.get("Model_Name", "N/A"),
                    "Temperature": data.get("Temperature", "N/A"),
                    "Version": data.get("Version", "N/A"),
                    "Date": data.get("Date", "N/A"),
                    "PDF Reader": data.get("PDF_Reader", "N/A"),
                    "Process Mode": data.get("Process_Mode", "N/A")
                }
            except Exception as e:
                print(f"Fehler beim Lesen der Datei {file}: {e}")
                return None
    return None

def show_selection_menu(base_directory) -> str:
    if not os.path.isdir(base_directory):
            print(f"Das Verzeichnis {base_directory} existiert nicht.")
            return

    
    clear_console()
    folder_list = [f for f in os.listdir(base_directory) if os.path.isdir(os.path.join(base_directory, f)) and not f.startswith(".")]

    if not folder_list:
        print("Es wurden keine gültigen Unterordner gefunden.")
        return

    print("\nDurchlauf-Übersicht:")
    table_data = []
    for i, folder in enumerate(folder_list, start=1):
        folder_path = os.path.join(base_directory, folder)
        json_data = read_json_from_folder(folder_path)
        if json_data:
            table_data.append([i, folder] + list(json_data.values()))

    headers = ["Nr.", "Folder", "Model Name", "Temperature", "Version", "Date", "PDF Reader", "Process Mode"]
    print(tabulate(table_data, headers=headers, tablefmt="grid"))

    try:
        choice = int(input("\nGeben Sie die Nummer des gewünschten Durchlaufs ein (oder 0 zum abbrechen): ")) - 1
        if choice == -1:
            print("Das Programm wird beendet.")
            raise("Abbruch...")
        if choice < 0 or choice >= len(folder_list):
            print("Ungültige Auswahl. Bitte versuchen Sie es erneut.")
            input("Drücken Sie die Eingabetaste, um fortzufahren...")
            show_selection_menu(base_directory)

        selected_folder = os.path.join(base_directory, folder_list[choice])
        selected_run = os.path.join(selected_folder, "*")

        return selected_run
    
    except ValueError:
        print("Ungültige Eingabe. Bitte geben Sie eine Zahl ein.")
        input("Drücken Sie die Eingabetaste, um fortzufahren...")
    

def main():
    parser = argparse.ArgumentParser(description='Process files with specified model (gpt or gemini).')
    parser.add_argument('--dir', required=True, help='Base Directory of the run data.')
    parser.add_argument('--combine7abc', action='store_true', help='Combines 7abc.')
    args = parser.parse_args()

    base_directory = args.dir
    combine7abc = args.combine7abc
    csv = "correct_answers_combined.csv" if combine7abc else "correct_answers.csv"

    while True:
        selected_run = show_selection_menu(base_directory)
        clear_console()
        result = run_comparrisson(csv, selected_run, combine7abc)
        print_result(result)
        input("\nDrücken Sie die Eingabetaste, um zur Übersicht zurückzukehren...")
        
if __name__ == "__main__":
    main()
