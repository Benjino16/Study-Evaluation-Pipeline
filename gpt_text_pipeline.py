from openai import OpenAI
from env_manager import env, getPrompt
from pdf_reader import get_text_from_pdf

assistantID = "asst_C4kxoXDv5DhL3Y4kPtxHoE7n"

def process_text_with_openai(filename: str, model: str, temp: float) -> str:
    # Process all prompts in a single request
    prompt = getPrompt()
    context = get_text_from_pdf(filename)

    client = OpenAI(
        api_key=env('API_GPT'),
    )
    response = client.chat.completions.create(
        model=model,
        temperature=temp,
        messages=[
            {"role": "user", "content": prompt + context}
        ]
    )
    return response.choices[0].message.content