import time
from env_manager import getPrompt, getPromptsLength
from gemini_pipeline import process_file_with_gemini
from gpt_pipeline import process_pdf_with_openai
from gpt_text_pipeline import process_text_with_openai

def run_request(file_path: str, model: str, process_all: bool, pdf_reader: bool, delay: int, temperature: float) -> str:

    if process_all:

        full_prompt = getPrompt()
        response = run_prompt(full_prompt, file_path, model, pdf_reader, temperature)
        return response
    
    else:
        results = []

        total_prompts = getPromptsLength()

        for i in range(total_prompts):
            prompt = getPrompt(i)
            try:
                response = run_prompt(prompt, file_path, model, pdf_reader, temperature)
                results.append(response)
            except Exception as e:
                print(f"Ein Fehler ist bei einer Single Prompt Anfrage aufgetreten! {e}")
                results.append("ERROR: SINGLE PROMPT REQUEST")

            if delay > 0:
                time.sleep(delay)
        return "\n".join(results)
    

def run_prompt(prompt: str, file_path: str, model: str, pdf_reader: bool, temperature: float):
    if model.lower().startswith('gemini'):
        if pdf_reader:
            exit("Eine Anfrage an gemini ist mit PDF-Reader nicht möglich.")
        else:
            last_output = process_file_with_gemini( prompt, file_path, model, temperature )

    elif model.lower().startswith('gpt'):
        if pdf_reader:
            last_output = process_text_with_openai( file_path, model, temperature)
        else:
            last_output = process_pdf_with_openai( prompt, file_path, model, temperature )

    elif model.lower().startswith('o1'):
        if pdf_reader:
            last_output = process_text_with_openai( file_path, model, temperature)
        else:
            exit("Eine Anfrage an ein o1 Modell ist ohne PDF-Reader nicht möglich.")
              
    return last_output