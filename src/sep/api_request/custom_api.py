"""
This script provides functionality to interact with a local Ollama API server.
It allows sending PDF content to models for processing, listing available models, 
and testing the API connection.
"""

import requests
import json
from sep.services.pdf_reader import get_text_from_pdf
from sep.logger import setup_logger
from sep.env_manager import env

log = setup_logger(__name__)

def process_text_with_custom_api(prompt: str, filename: str, model: str, temp: float) -> str:
    """
    Processes a PDF file using the specified model via the Ollama API.
    
    Returns:
        str: Model's response text.
    """

    custom_api_key  = env("CUSTOM_API_KEY")
    custom_api_url = env("CUSTOM_API_URL")

    if custom_api_url is None:
        raise Exception("CUSTOM_API_URL environment variable is not set")
    if custom_api_key is None:
        raise Exception("CUSTOM_API_KEY environment variable is not set")


    context = get_text_from_pdf(filename)

    headers = {
        "Authorization": f"Bearer {custom_api_key}",
        "Content-Type": "application/json"
    }

    data = {
        "model": model,
        "messages": [
            {
                "role": "system",
                "content": prompt,
            },
            {
                "role": "user",
                "content": context,
            }
        ],
        "temperature": temp,
        "stream": False
    }
    json_data = json.dumps(data)
    response = requests.post(url=custom_api_url, data=json_data, headers=headers)
    if response.status_code == 200:
        return response.json()['response']
    
    raise requests.exceptions.RequestException(f"Response status-code: {response.status_code}")
