import time
from env_manager import getPrompt, getPromptsLength
from gemini_pipeline import process_file_with_gemini
from gpt_pipeline import process_pdf_with_openai

def run_request(file_path: str, model: str = "gemini-1.5-pro", process_all: bool = True, delay: int = 0) -> str:

    if process_all:

        full_prompt = getPrompt()
        response = run_prompt(full_prompt, file_path, model)
        return response
    
    else:
        results = []

        total_prompts = getPromptsLength()

        for i in range(total_prompts):
            prompt = getPrompt(i)
            try:
                response = run_prompt(prompt, file_path, model)
                results.append(response)
            except Exception as e:
                print(f"Ein Fehler ist bei einer Single Prompt Anfrage aufgetreten! {e}")
                results.append("ERROR: SINGLE PROMPT REQUEST")

            if delay > 0:
                time.sleep(delay)
        return "\n".join(results)
    

def run_prompt(prompt: str, file_path: str, model):
    if model.lower().startswith('gemini'):
        last_output = process_file_with_gemini(
            prompt, file_path, model
        )
    elif model.lower().startswith('gpt'):
        last_output = process_pdf_with_openai(
            prompt, file_path, model
        )
    return last_output