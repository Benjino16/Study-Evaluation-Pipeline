import os
from env_manager import env
import google.generativeai as genai

genai.configure(api_key=env('API_GEMINI'))

# Global list to check for already uploaded pdfs
uploaded_files = []

def get_filename_without_path_and_extension(filepath: str) -> str:
    """Extrahiert den Dateinamen ohne Pfad und Erweiterung."""
    return os.path.splitext(os.path.basename(filepath))[0]

def process_file_with_gemini(prompt: str, filename: str, model: str, temperature: float) -> str:
    global uploaded_files
    
    # Extrahiere Dateinamen ohne Pfad und Erweiterung
    file_key = get_filename_without_path_and_extension(filename)

    # Überprüfen, ob das PDF bereits hochgeladen wurde
    for uploaded_file in uploaded_files:
        if uploaded_file["name"] == file_key:
            print(f"Datei '{file_key}' wurde bereits hochgeladen, verwende gespeichertes File.")
            file = uploaded_file["file"]
            break
    else:
        # Datei hochladen, falls noch nicht in der Liste vorhanden
        sample_file = genai.upload_file(path=filename, display_name="Gemini PDF FILE")
        print(f"Hochgeladene Datei '{sample_file.display_name}' als: {sample_file.uri}")

        # Datei zur Liste hinzufügen
        uploaded_files.append({
            "name": file_key,
            "file": sample_file
        })
        file = sample_file

    # Modell definieren und Antwort generieren
    model = genai.GenerativeModel(model_name=model)

    response = model.generate_content(
        [file, prompt],
        generation_config=genai.types.GenerationConfig(
            temperature=temperature,
        )
    )
    return response.text

def test_gemini_pipeline():
    try:
        model = genai.GenerativeModel(model_name="gemini-1.5-flash")
        response = model.generate_content(
            "This is a test call. Simply answer with the word test.",
        )
        return response.text != None
    except Exception as e:
        print(e)
        return False