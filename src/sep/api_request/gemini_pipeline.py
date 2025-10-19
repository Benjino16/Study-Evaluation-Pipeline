import os
from sep.env_manager import env
from google import genai
import logging

logging.basicConfig(level=logging.INFO)

client = genai.Client(api_key=env('API_GEMINI'))

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
        file  = client.files.upload(file=filename)
        logging.info(f"Uploaded file '{file.display_name}' as: {file.uri}")

        # Add the file to the list
        uploaded_files.append({
            "name": file_key,
            "file": file
        })

    contents = [
        {
            "role": "user",
            "parts": [
                {"file_data": {"file_uri": file.uri}},
                {"text": prompt},
            ],
        }
    ]

    response = client.models.generate_content(
        model=model,
        contents=contents,
        config={"temperature": temperature},
    )
    return response.text

def test_gemini_pipeline():
    """
    Tests the Gemini pipeline by making a test call and checking if it responds correctly.
    """
    try:
        response = client.models.generate_content(
            model="gemini-1.5-flash",
            contents=[{"role": "user", "parts": [{"text": "This is a test call. Simply answer with the word test."}]}]
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
