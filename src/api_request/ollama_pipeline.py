"""
This script provides functionality to interact with a local Ollama API server.
It allows sending PDF content to models for processing, listing available models, 
and testing the API connection.
"""

import requests
import json
from src.prompt_manager import getPrompt
from src.services.pdf_reader import get_text_from_pdf
import logging

logging.basicConfig(level=logging.INFO)

api_url = 'https://quest-gpu-06.charite.de/api/generate'

def process_text_with_ollama(filename: str, model: str, temp: float) -> str:
    """
    Processes a PDF file using the specified model via the Ollama API.
    
    Returns:
        str: Model's response text.
    """
    # Process all prompts in a single request
    prompt = getPrompt()
    context = get_text_from_pdf(filename)

    data = {
        "model": model,
        "prompt": f"[PDF Context START] {context} [PDF Context END] \n\n[Prompt] {prompt}",
        "temperature": temp,
        "stream": False
    }
    json_data = json.dumps(data)
    response = requests.post(api_url, json_data)
    if response.status_code == 200:
        return response.json()['response']
    
    raise requests.exceptions.RequestException(f"Response status-code: {response.status_code}")

def list_models():
    """
    Lists all available models from the Ollama API.

    Returns:
        list: A list of available model names.
    """
    response = requests.get('https://quest-gpu-06.charite.de/api/tags', headers={'Content-Type': 'application/json'})
    response.raise_for_status()
    models = response.json().get('models', [])
    models = [model['name'] for model in models]
    return models

def test_ollama_pipeline():
    """
    Tests the Ollama API connection by sending a simple prompt.

    Returns:
        bool: True if the request succeeds, False otherwise.
    """
    try:
        data = {
            "model": "llama3.3:latest",
            "prompt": "What is 5 + 5?",
            "stream": False
        }
        json_data = json.dumps(data)
        response = requests.post(api_url, json_data)
        if response.status_code == 200:
            logging.info(response.json()['response'])
            return response is not None
        else:
            raise requests.exceptions.RequestException(f"Response status-code: {response.status_code}")
    except Exception:
        logging.exception("Error while using local pipeline")
        return False

if __name__ == "__main__":
    models = list_models()
    print(models)
