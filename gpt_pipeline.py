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

assistantID = "asst_C4kxoXDv5DhL3Y4kPtxHoE7n"

def process_pdf_with_openai(filename: str, model: str = "gpt-4o", process_all: bool = True, delay: int = 0) -> str:
    client = OpenAI(
        api_key=env('API_GPT'),
    )

    pdf_assistant = client.beta.assistants.retrieve(assistantID)
    
    thread = client.beta.threads.create()
    
    file_id = get_file(filename, client)

    if process_all:
        # Process all prompts in a single request
        prompt = getPrompt()
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
            thread_id=thread.id, assistant_id=pdf_assistant.id, timeout=20000
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
            
    else:
        # Process each prompt separately
        results = []
        total_prompts = getPromptsLength()

        for i in range(total_prompts): # Send each prompt as a separate request
            prompt = getPrompt(i)

            try:
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
                    thread_id=thread.id, assistant_id=pdf_assistant.id, timeout=20000
                )

                if run.status == "completed":
                    messages_cursor = client.beta.threads.messages.list(thread_id=thread.id)
                    messages = [message for message in messages_cursor]
                    res_txt = messages[0].content[0].text.value
                    
                    results.append(res_txt)

                else:
                    print(f"Run failed with \n status: {run.status} \n error: {run.last_error}n")

            except Exception as e:
                print(f"Warning for prompt {i}: {str(e)} - Skipping this prompt")

            if delay > 0:
                time.sleep(delay)

        return "\n".join(results)
    
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