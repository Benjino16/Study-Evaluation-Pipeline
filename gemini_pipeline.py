import os
from env_manager import env
import google.generativeai as genai
import logging

logging.basicConfig(level=logging.INFO)
genai.configure(api_key=env('API_GEMINI'))

# Global list to check for already uploaded pdfs
uploaded_files = []

def get_filename_without_path_and_extension(filepath: str) -> str:
    """
    Extracts the filename without the path and extension.
    """
    return os.path.splitext(os.path.basename(filepath))[0]

def process_file_with_gemini(prompt: str, filename: str, model: str, temperature: float) -> str:
    """
    Processes the file with Gemini model by uploading it if not already uploaded, 
    and generates content based on the prompt.
    """
    global uploaded_files
    
    # Extract filename without path and extension
    file_key = get_filename_without_path_and_extension(filename)

    # Check if the PDF has already been uploaded
    for uploaded_file in uploaded_files:
        if uploaded_file["name"] == file_key:
            logging.info(f"File '{file_key}' was already uploaded. Using the saved version instead.")
            file = uploaded_file["file"]
            break
    else:
        # Upload file if not present in the list
        sample_file = genai.upload_file(path=filename, display_name="Gemini PDF FILE")
        logging.info(f"Uploaded file '{sample_file.display_name}' as: {sample_file.uri}")

        # Add the file to the list
        uploaded_files.append({
            "name": file_key,
            "file": sample_file
        })
        file = sample_file

    # Define the model and generate the response
    model = genai.GenerativeModel(model_name=model)

    response = model.generate_content(
        [file, prompt],
        generation_config=genai.types.GenerationConfig(
            temperature=temperature,
        )
    )
    return response.text

def test_gemini_pipeline():
    """
    Tests the Gemini pipeline by making a test call and checking if it responds correctly.
    """
    try:
        model = genai.GenerativeModel(model_name="gemini-1.5-flash")
        response = model.generate_content(
            "This is a test call. Simply answer with the word test.",
        )
        return response.text != None
    except Exception as e:
        logging.exception("Exception while trying to test gemini api.")
        return False
    
def get_gemini_model_name(model: str) -> str:
    """
    Fetches the model information and returns the model name.
    (The real version is a TODO item)
    """
    model_info = genai.get_model("models/" + model)
    return model #TODO GET REAL MODEL VERSION
