import requests
import json
from env_manager import getPrompt
from pdf_reader import get_text_from_pdf

api_url = 'https://quest-gpu-06.charite.de/api/generate'

def process_text_with_ollama(filename: str, model: str, temp: float) -> str:
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
    else:
        raise Exception(response.text)
    
    return response

def list_models():
    response = requests.get('https://quest-gpu-06.charite.de/api/tags', headers={'Content-Type': 'application/json'})
    response.raise_for_status()
    models = response.json().get('models', [])
    models = [model['name'] for model in models]
    return models

def test_ollama_pipeline():
    try:
        data = {
            "model": "llama3.3:latest",
            "prompt": "What is 5 + 5?",
            "stream": False
        }
        json_data = json.dumps(data)
        response = requests.post(api_url, json_data)
        if response.status_code == 200:
            print(response.json()['response'])
            return response != None
        else:
            raise Exception(response.text)
    except Exception as e:
        print(e)
        return False

if __name__ == "__main__":
    models = list_models()
    print(models)