import time
from openai import OpenAI
from env_manager import env, getPrompt, getPromptsLength
from evaluation import evaluate_csv_string
from openai.types.beta.threads.message_create_params import (
    Attachment,
    AttachmentToolFileSearch,
)
import os
from gpt_file_manager import get_file

assistantID = "asst_IU1BLwiptkX3J4fj5f2wRfaI"

client = OpenAI(
        api_key=env('API_GPT'),
    )

def process_pdf_with_openai(prompt: str, filename: str, model: str, temperature: float) -> str:

    pdf_assistant = client.beta.assistants.retrieve(assistantID)
    
    thread = client.beta.threads.create()
    
    file_id = get_file(filename, client)

    client.beta.threads.messages.create(
        thread_id=thread.id,
        role="user",
        attachments=[
            Attachment(
                file_id=file_id, tools=[AttachmentToolFileSearch(type="file_search")]
            )
        ],
        content=prompt,
    )

    run = client.beta.threads.runs.create_and_poll(
        thread_id=thread.id, assistant_id=pdf_assistant.id, timeout=20000, temperature=temperature
    )

    if run.status == "completed":
        messages_cursor = client.beta.threads.messages.list(thread_id=thread.id)
        messages = [message for message in messages_cursor]
        res_txt = messages[0].content[0].text.value

        print("Res Text: " + res_txt)
        
        if not res_txt.strip():
            raise Exception(f"Completed run but received empty or malformed response for {filename}.\n status: {run.status} \n error: {run.last_error}")
            
        return res_txt
    else:
        raise Exception(f"Run failed with \n status: {run.status} \n error: {run.last_error}")
    
def test_gpt_pipeline():
    try:
        client = OpenAI(
            api_key=env('API_GPT'),
        )
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "user", "content": "This is a test call. Simply answer with the word test."}
            ]
        )
        return response.choices[0].message.content != None
    except:
        return False