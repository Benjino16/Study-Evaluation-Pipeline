import os
import yaml
from dotenv import load_dotenv, find_dotenv

dotenv_path = find_dotenv('.env')
config_path = "config.yaml"
load_dotenv(dotenv_path)

def config(key):
    with open(config_path, 'r') as f:
        settings = yaml.safe_load(f)
    
    parts = key.split(".")
    value = settings
    for part in parts:
        value = value.get(part)
        if value is None:
            raise KeyError(f"Key '{key}' not found in {config_path}")
    
    return value


PROMPT_PATH = config("prompt_file_path")
GPT_UPLOADED_FILES = config("uploaded_gpt_files")

PDF_FOLDER = config("pdf_folder")
RESULT_FOLDER = config("result_folder")
CSV_PATH = config("csv_folder")



def env(key):
    return os.getenv(key)

def getPDFPath(number: str):
    return f"{PDF_FOLDER}{number.zfill(4)}.pdf"

def load_valid_models():
    with open(config_path) as f:
        config = yaml.safe_load(f)
        valid_models = config['valid_models']
        return valid_models