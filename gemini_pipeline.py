import os
from env_manager import env, getPrompt
from evaluation import evaluate_csv_string
import google.generativeai as genai
import time
from env_manager import env, getPrompt, getPromptsLength

genai.configure(api_key=env('API_GEMINI'))

temp = 0.0

def process_file_with_gemini(filename: str, model: str = "gemini-1.5-pro", process_all: bool = True, delay: int = 0) -> str:
    

    sample_file = genai.upload_file(path=filename, display_name="Gemini 1.5 PDF")
    print(f"Uploaded file '{sample_file.display_name}' as: {sample_file.uri}")

    file = genai.get_file(name=sample_file.name)
    print(f"Retrieved file '{file.display_name}' as: {file.uri}")
    
    model = genai.GenerativeModel(model_name=model)

    if process_all:
        prompt = getPrompt()
        response = model.generate_content(
            [sample_file, prompt],
            generation_config=genai.types.GenerationConfig(
            temperature=temp,
            )
        )
        return response.text
    else:
        # Process each prompt separately
        results = []
        total_prompts = getPromptsLength()

        for i in range( total_prompts): # Send each prompt as a separate request
            prompt = getPrompt(i)

            try:
                print(f"Sending prompt: \n '{prompt}")
                response = model.generate_content(
                    [sample_file, prompt],
                    generation_config=genai.types.GenerationConfig(
                    temperature=temp,
                    )
                )

                if response.text is not None:
                    results.append(response.text)

                else:
                    print(f"Warning for prompt {i}: empty result")

            except Exception as e:
                print(f"Warning for prompt {i}: {str(e)} - Skipping this prompt")

            if delay > 0:
                time.sleep(delay)

        return "\n".join(results)
    
def test_gemini_pipeline():
    try:
        model = genai.GenerativeModel(model_name="gemini-1.5-flash")
        response = model.generate_content(
            "This is a test call. Simply answer with the word test.",
        )
        return response.text != None
    except:
        return False