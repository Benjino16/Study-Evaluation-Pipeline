import json
import os
from openai import OpenAI
import env_manager


uploaded_files = env_manager.GPT_UPLOADED_FILES

def get_file(file_path: str, client: object):

    file_name = os.path.splitext(os.path.basename(file_path))[0]
    
    file_id = get_file_from_json(file_name)
    
    if file_id is None:
        with open(file_path, "rb") as f:
            file = client.files.create(file=f, purpose="assistants")
        
        add_file_to_json(file_name, file.id)
        return file.id
    
    return file_id

def add_file_to_json(file_name: str, file_id: str):
    if not os.path.exists(uploaded_files):
        with open(uploaded_files, "w") as f:
            json.dump([], f)

    with open(uploaded_files, "r") as f:
        data = json.load(f)
    
    data.append({"file_name": file_name, "file_id": file_id})

    with open(uploaded_files, "w") as f:
        json.dump(data, f, indent=4)

def get_file_from_json(file_name: str):
    if not os.path.exists(uploaded_files):
        return None

    with open(uploaded_files, "r") as f:
        data = json.load(f)
    
    for entry in data:
        if entry["file_name"] == file_name:
            return entry["file_id"]

    return None
