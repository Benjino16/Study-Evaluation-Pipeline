"""
This script interacts with the OpenAI API and processes PDF files using an assistant model.
It includes functions to process a PDF with OpenAI, test the GPT pipeline, and get the GPT model name.
"""

from openai import OpenAI
from env_manager import env
from openai.types.beta.threads.message_create_params import (
    Attachment,
    AttachmentToolFileSearch,
)
import os
from gpt_file_manager import get_file
import logging

logging.basicConfig(level=logging.INFO)

# Assistant ID for interacting with the OpenAI Assistant
assistantID = "asst_IU1BLwiptkX3J4fj5f2wRfaI"

# Initialize the OpenAI client with the API key
client = OpenAI(
        api_key=env('API_GPT'),
    )

def process_pdf_with_openai(prompt: str, filename: str, model: str, temperature: float) -> str:
    """
    Processes a PDF file with OpenAI using the specified prompt and model parameters.

    Returns:
        str: The result text from the OpenAI assistant.

    Raises:
        Exception: If the OpenAI processing fails or if the response is malformed.
    """
    pdf_assistant = client.beta.assistants.retrieve(assistantID)
    
    # Create a new thread for the processing
    thread = client.beta.threads.create()
    
    # Get the file ID for the PDF
    file_id = get_file(filename, client)

    # Send the file and prompt to the assistant
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

    # Run the assistant and wait for the response
    run = client.beta.threads.runs.create_and_poll(
        thread_id=thread.id, assistant_id=pdf_assistant.id, timeout=20000, temperature=temperature
    )

    # If the run is successful, extract the response text
    if run.status == "completed":
        messages_cursor = client.beta.threads.messages.list(thread_id=thread.id)
        messages = [message for message in messages_cursor]
        res_txt = messages[0].content[0].text.value

        logging.info("Res Text: " + res_txt)
        
        # Raise an exception if the response text is empty or malformed
        if not res_txt.strip():
            raise Exception(f"Completed run but received empty or malformed response for {filename}.\n status: {run.status} \n error: {run.last_error}")
            
        return res_txt
    else:
        raise Exception(f"Run failed with \n status: {run.status} \n error: {run.last_error}")
    
def test_gpt_pipeline():
    """
    Tests if the GPT pipeline is functioning by sending a simple test prompt.

    Returns:
        bool: True if the pipeline is working, False if an error occurs.
    """
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
    except Exception:
        logging.exception("Exception while trying to test gpt api.")
        return False
    
def get_gpt_model_name(model: str) -> str:
    """
    Gets the name of the GPT model used for a test call.
    
    Returns:
        str: The name of the GPT model used.
    """
    client = OpenAI(
        api_key=env('API_GPT'),
    )
    response = client.chat.completions.create(
        model=model,
        messages=[
            {"role": "user", "content": "This is a test call. Simply answer with the word test."}
        ]
    )

    return response.model
