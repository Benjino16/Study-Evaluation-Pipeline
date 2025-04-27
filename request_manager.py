import time
from prompt_manager import getPrompt, getPromptsLength
from gemini_pipeline import process_file_with_gemini
from gpt_pipeline import process_pdf_with_openai
from gpt_text_pipeline import process_text_with_openai
from ollama_pipeline import process_text_with_ollama
import logging

logging.basicConfig(level=logging.INFO)

def run_request(file_path: str, model: str, process_all: bool, pdf_reader: bool, delay: int, temperature: float) -> str:
    """Returns the raw output of the model and the used prompt."""

    if process_all:

        full_prompt = getPrompt()
        response = run_prompt(full_prompt, file_path, model, pdf_reader, temperature)
        return response, full_prompt
    
    else:
        results = []

        total_prompts = getPromptsLength()

        for i in range(total_prompts):
            prompt = getPrompt(i)
            try:
                response = run_prompt(prompt, file_path, model, pdf_reader, temperature)
                results.append(response)
            except Exception:
                logging.exception(f"An error has occurred with a single prompt request!")
                results.append("ERROR: SINGLE PROMPT REQUEST")

            if delay > 0:
                time.sleep(delay)
        return "\n".join(results), "splitted prompt request"
    

def run_prompt(prompt: str, file_path: str, model: str, pdf_reader: bool, temperature: float):
    if model.lower().startswith('gemini'):
        if pdf_reader:
            raise ValueError("A request to gemini is not possible with a PDF reader. Do not use --pdf_reader in the arguments.")
        else:
            last_output = process_file_with_gemini( prompt, file_path, model, temperature )

    elif model.lower().startswith('gpt') or model.lower().startswith('deepseek-chat'):
        if pdf_reader:
            last_output = process_text_with_openai( file_path, model, temperature)
        else:
            last_output = process_pdf_with_openai( prompt, file_path, model, temperature )

    elif model.lower().startswith('o1'):
        if pdf_reader:
            last_output = process_text_with_openai( file_path, model, temperature)
        else:
            raise ValueError("A request to an o1 model is not possible without a PDF reader. Use --pdf_reader in the arguments.")
    elif model.lower().startswith('deepseek'):
        if pdf_reader:
            last_output = process_text_with_ollama( file_path, model, temperature)
        else:
            raise ValueError("A request to an ollama model is not possible without a PDF reader. Use --pdf_reader in the arguments.")
              
    return last_output