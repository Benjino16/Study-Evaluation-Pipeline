"""
This script manages the batch processing of PDF or text files using different language models (e.g., GPT, Gemini).
It supports reading from local PDFs, sending data to a model via API requests, and saving raw model responses.
"""

from sep.env_manager import load_valid_models, RESULT_FOLDER
from sep.core.api_request.request_manager import run_request
from sep.core.evaluation.save_raw_data import save_raw_data_as_json
from sep.core.services.pdf_reader import get_pdf_reader_version

import os
import datetime

# Supported Models
VALID_MODELS = load_valid_models()

SAVING_PATH = None


def process_paper(prompt: str, model: str, file_path: str, delay = 15, temp = 1.0, single_process = False, pdf_reader = False, same_run = False):
    """
    Processes a PDF file using a specified model and prompt.
    """
    global SAVING_PATH
    if not same_run or SAVING_PATH is None:
        timestamp = datetime.datetime.now().strftime("%Y%m%d-%H%M%S")
        save_folder = RESULT_FOLDER + f"{model}-temp{temp}-{timestamp}/"
        SAVING_PATH = save_folder


    if not os.path.isfile(file_path):
        error_message = f"{file_path}, not a valid file."
        raise ValueError(error_message)

    if model not in VALID_MODELS:
        raise ValueError(
            f"Error: Invalid model '{model}' specified. Supported models are: {', '.join(VALID_MODELS)}")



    if pdf_reader:
        pdf_reader_version = get_pdf_reader_version()
    else:
        pdf_reader_version = '-'

    if single_process:
        process_mode = "process full pdf with prompt-split requests"
    else:
        process_mode = "process full pdf in single request"

    last_output = run_request(prompt, file_path, model, not single_process, pdf_reader, delay, temp)

    if last_output is None:
        raise Exception(f"Evaluation for {file_path} failed due to processing error.")

    save_raw_data_as_json(
        raw_data=last_output,
        pdf_name=os.path.basename(file_path),
        model_name=model,
        temp=temp,
        pdf_reader=pdf_reader,
        pdf_reader_version=pdf_reader_version,
        process_mode=process_mode,
        prompt=prompt,
        save_folder=SAVING_PATH)

    return last_output, SAVING_PATH