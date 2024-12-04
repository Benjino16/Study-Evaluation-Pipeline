import os
import platform
from compare_answers import run_comparrisson

def clear_console():
    # Funktion zum Leeren der Konsole, abhängig vom Betriebssystem
    if platform.system() == "Windows":
        os.system("cls")
    else:
        os.system("clear")

def main():
    base_directory = "../Data/Results/"

    # Prüfen, ob das Verzeichnis existiert
    if not os.path.isdir(base_directory):
        print(f"Das Verzeichnis {base_directory} existiert nicht.")
        return

    while True:
        clear_console()
        
        # Liste der Ordner im angegebenen Verzeichnis
        folder_list = [f for f in os.listdir(base_directory) if os.path.isdir(os.path.join(base_directory, f))]

        # Prüfen, ob es Unterordner gibt
        if not folder_list:
            print("Es wurden keine Unterordner gefunden.")
            return

        # Ausgabe der Ordnerliste
        print("\nBitte wählen Sie einen der folgenden Ordner aus (oder beenden Sie das Programm):")
        for i, folder in enumerate(folder_list, start=1):
            print(f"{i}. {folder}")
        print(f"{len(folder_list) + 1}. Programm beenden")

        try:
            # Eingabe des Benutzers
            choice = int(input("\nGeben Sie die Nummer des gewünschten Ordners ein: ")) - 1

            if choice == len(folder_list):
                print("Das Programm wird beendet.")
                break

            if choice < 0 or choice > len(folder_list):
                print("Ungültige Auswahl. Bitte versuchen Sie es erneut.")
                input("Drücken Sie die Eingabetaste, um fortzufahren...")
                continue

            selected_folder = os.path.join(base_directory, folder_list[choice])

            # Pfad zur CSV-Datei und Datenpfad
            csv = "correct_answers.csv"
            data = os.path.join(selected_folder, "*")
            combine7abc = False

            # Konsole leeren vor dem Start der Methode
            clear_console()

            # Methode aus compare_answers.py aufrufen
            run_comparrisson(csv, data, combine7abc)

            # Nach der Ausführung warten, um zurückzukehren oder zu beenden
            print("\nAktion abgeschlossen. Was möchten Sie tun?")
            print("1. Zurück zur Ordnerliste")
            print("2. Programm beenden")

            next_action = input("\nGeben Sie die Nummer Ihrer Wahl ein: ")

            if next_action == "2":
                print("Das Programm wird beendet.")
                break

        except ValueError:
            print("Ungültige Eingabe. Bitte geben Sie eine Zahl ein.")
            input("Drücken Sie die Eingabetaste, um fortzufahren...")

if __name__ == "__main__":
    main()
