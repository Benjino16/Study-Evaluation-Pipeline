import time
from openai import OpenAI
from env_manager import env, getPrompt, getPromptsLength
from evaluation import evaluate_csv_string
from gpt_file_manager import get_file
from pdf_reader import get_text_from_pdf

assistantID = "asst_C4kxoXDv5DhL3Y4kPtxHoE7n"

def process_text_with_openai(filename: str, model: str = "gpt-4o", process_all: bool = True, delay: int = 0) -> str:
    if process_all:
        # Process all prompts in a single request
        prompt = getPrompt()
        context = get_text_from_pdf(filename)

        client = OpenAI(
            api_key=env('API_GPT'),
        )
        response = client.chat.completions.create(
            model=model,
            messages=[
                {"role": "user", "content": prompt + context}
            ]
        )
        return response.choices[0].message.content