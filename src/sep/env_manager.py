import os
import yaml
from dotenv import load_dotenv, find_dotenv
from pathlib import Path
from sep.logger import setup_logger

log = setup_logger(__name__)

"""The environment manager takes care of the correct import of the env variables and the loading of config.yaml."""

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent

dotenv_path = find_dotenv(PROJECT_ROOT / '.env')
config_path = PROJECT_ROOT / 'configs' / 'config.yaml'
load_dotenv(dotenv_path)

def config(key):
    """Loads a variable from the config.yaml with the given key."""
    with open(config_path, 'r') as f:
        settings = yaml.safe_load(f)
    
    parts = key.split(".")
    value = settings
    for part in parts:
        value = value.get(part)
        if value is None:
            log.warning(f"The key {key} was not found in the config.yaml")
    
    return value


# VARIABLES FROM CONFIG
PROMPT_PATH = config("prompt_file_path")
GPT_UPLOADED_FILES = config("uploaded_gpt_files")
BASIC_PROMPT_PATH = config("basic_prompt_file_path")
PROMPT_DESIGN_PROMPT_PATH = config("prompt_design_prompt_path")

PDF_FOLDER = PROJECT_ROOT / config("pdf_folder")
RESULT_FOLDER = config("result_folder")
CSV_FOLDER = config("csv_folder")
ADJUSTED_PROMPT_FOLDER = config("adjusted_prompts")
DEFAULT_CSV = config("standard_csv_responses")
DEFAULT_CSV_COMBINED = config("standard_csv_responses_7abc_combined")


def env(key):
    """Returns the value from the .env file with the given key."""
    return os.getenv(key)

def getPDFPath(number: str):
    """Returns the path of the PDF with the specified study number."""
    return f"{PDF_FOLDER}{number.zfill(4)}.pdf"

def load_valid_models():
    """Loads the list with the valid models from config.yml."""
    with open(config_path) as f:
        config = yaml.safe_load(f)
        valid_models = config['valid_models']
        return valid_models