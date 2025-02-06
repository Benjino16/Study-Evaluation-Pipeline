from openai import OpenAI
from env_manager import env, getPrompt
from pdf_reader import get_text_from_pdf

def process_text_with_openai(filename: str, model: str, temp: float) -> str:
    # Process all prompts in a single request
    prompt = getPrompt()
    context = get_text_from_pdf(filename)
    client = None

    if model == 'deepseek-chat':
        client = OpenAI(
            api_key=env('API_DEEPSEEK'),
            base_url="https://api.deepseek.com"
        )
    else:
        client = OpenAI(
            api_key=env('API_GPT'),
        )
    response = client.chat.completions.create(
        model=model,
        temperature=temp,
        messages=[
            {"role": "system", "content": prompt},
            {"role": "user", "content": context}
        ],
        stream=False
    )
    return response.choices[0].message.content

def test_deepseek_pipeline():
    try:
        client = OpenAI(
            api_key=env('API_DEEPSEEK'),
            base_url="https://api.deepseek.com"
        )
        response = client.chat.completions.create(
        model='deepseek-chat',
        messages=[
            {"role": "user", "content": "This is a test call. Simply answer with the word test."}
        ],
        stream=False
    )
        return response.choices[0].message.content != None
    except:
        return False