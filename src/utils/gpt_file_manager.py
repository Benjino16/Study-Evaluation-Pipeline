import json
import os
from openai import OpenAI
from src import env_manager

# This script handles file management for uploaded files, including retrieving, storing, and checking for previously uploaded files
# for a given file. It interacts with the OpenAI client to upload files if they haven't been uploaded already.

uploaded_files = env_manager.GPT_UPLOADED_FILES

def get_file(file_path: str, client: object):
    """
    Retrieves the file ID for a given file. If the file has not been uploaded yet, it uploads the file to the client and stores its ID.
    
    Returns:
        str: The file ID of the uploaded or retrieved file.
    """
    file_name = os.path.splitext(os.path.basename(file_path))[0]
    
    file_id = get_file_from_json(file_name)
    
    if file_id is None:
        with open(file_path, "rb") as f:
            file = client.files.create(file=f, purpose="assistants")
        
        add_file_to_json(file_name, file.id)
        return file.id
    
    return file_id

def add_file_to_json(file_name: str, file_id: str):
    """
    Adds a new file's name and ID to the JSON file that keeps track of uploaded files.
    """
    if not os.path.exists(uploaded_files):
        with open(uploaded_files, "w") as f:
            json.dump([], f)

    with open(uploaded_files, "r") as f:
        data = json.load(f)
    
    data.append({"file_name": file_name, "file_id": file_id})

    with open(uploaded_files, "w") as f:
        json.dump(data, f, indent=4)

def get_file_from_json(file_name: str):
    """
    Retrieves the file ID for a given file name from the JSON file.

    Returns:
        str or None: The file ID if the file exists, or None if the file is not found.
    """
    if not os.path.exists(uploaded_files):
        return None

    with open(uploaded_files, "r") as f:
        data = json.load(f)
    
    for entry in data:
        if entry["file_name"] == file_name:
            return entry["file_id"]

    return None
