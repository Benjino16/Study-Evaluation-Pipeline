"""
This script manages the batch processing of PDF or text files using different language models (e.g., GPT, Gemini).
It supports reading from local PDFs, sending data to a model via API requests, and saving raw model responses.
Additional features include live status updates, error logging, and configurable processing modes via command-line arguments.
"""

from env_manager import load_valid_models
from prompt_manager import getPromptsLength
from request_manager import run_request
from save_raw_data import save_raw_data_as_json
from pdf_reader import get_pdf_reader_version

import argparse
import glob
import os
import time
import sys
import datetime
import traceback

# Supported Models
VALID_MODELS = load_valid_models()

def clear_console():
    """
    Clears the console output.
    """
    os.system('cls' if os.name == 'nt' else 'clear')

def display_overview(model: str, files_to_process, delay: int, process_all: bool, temperature: float):
    """
    Displays a summary of the current processing configuration.

    """
    clear_console()
    if process_all:
        time_calculation = (delay + 5) * len(files_to_process)
    else:
        time_calculation = (delay + 5) * len(files_to_process) * getPromptsLength()

    formatted_time = str(datetime.timedelta(seconds=time_calculation))

    print("\n-------- Overview --------\n")
    print(f"Model: {model}")
    print(f"Temperature: {temperature}")
    print(f"Files: {files_to_process}")
    print(f"Delay between requests: {delay}")
    print(f"Process all prompts: {process_all}")
    print(f"Estimated Total Time: {formatted_time}")

def display_status(model, current_file, progress, failed, errors, last_output):
    """
    Displays the current processing status, last output, and any errors.
    """
    clear_console()
    print(f"Model: {model}")
    print(f"File: {current_file}")
    print(f"Progress: {progress}")
    print(f"Failed: {failed}\n")
    
    print("\n-------- Last Answer --------\n")
    print(last_output or "Waiting for output...")
    
    if errors:
        print("\n-------- Errors --------\n")
        for error in errors:
            print(error)
            
    print("\n-------- Live Protocol --------\n")

def main():
    """
    Main entry point for processing files with a specified model.
    Parses command-line arguments, validates input, manages processing flow, and saves results.
    """
    parser = argparse.ArgumentParser(description='Process files with specified model (e.g., gpt or gemini).')
    parser.add_argument('--model', required=True, help='Model to use (e.g., gpt-4o, gemini-3).')
    parser.add_argument('--files', nargs='+', required=True, help='Files or patterns to process (supports globbing).')
    parser.add_argument('--delay', type=int, default=15, help='Delay time in seconds between processing files.')
    parser.add_argument('--temp', type=float, default=1.0, help='The temperature setting for model randomness.')
    parser.add_argument('--single_process', action='store_true', help='Process all prompts in splitted request if set. If --pdf_reader is enabled, it processes each page separately.')
    parser.add_argument('--pdf_reader', action='store_true', help='Uses a local PDF reader to extract content as context for the model.')

    args = parser.parse_args()

    if args.model not in VALID_MODELS:
        raise ValueError(f"Error: Invalid model '{args.model}' specified. Supported models are: {', '.join(VALID_MODELS)}")

    files_to_process = []
    for file_pattern in args.files:
        files_to_process.extend(glob.glob(file_pattern))

    files_to_process = list(set(files_to_process))  # Remove duplicate files

    # Get PDF reader version if necessary
    if args.pdf_reader:
        pdf_reader_version = get_pdf_reader_version()
    else:
        pdf_reader_version = '-'

    # Determine processing mode
    if args.single_process:
        process_mode = "process full pdf with prompt-split requests"
    else:
        process_mode = "process full pdf in single request"

    # Show processing overview
    display_overview(args.model, files_to_process, args.delay, not args.single_process, args.temp)
    user_input = input("Press Enter to continue...")
    if user_input != "":
        raise ValueError("Exiting program, user pressed a key other than Enter.")

    total_files = len(files_to_process)
    processed_count = 0
    failed_count = 0
    errors = []

    # Process each file
    for file_path in files_to_process:
        processed_count += 1
        last_output = None
        
        if not os.path.isfile(file_path):
            error_message = f"Skipping {file_path}, not a valid file."
            errors.append(error_message)
            failed_count += 1
            display_status(args.model, os.path.basename(file_path), 
                           f"{processed_count}/{total_files}", failed_count, errors, last_output)
            continue

        try:
            last_output, prompt = run_request(file_path, args.model, not args.single_process, args.pdf_reader, args.delay, args.temp)
                
            if last_output is None:
                raise Exception(f"Skipping evaluation for {file_path} due to processing error.")
            
            save_raw_data_as_json(
                raw_data=last_output, 
                pdf_name=os.path.basename(file_path), 
                model_name=args.model,
                temp=args.temp,
                pdf_reader=args.pdf_reader,
                pdf_reader_version=pdf_reader_version,
                process_mode=process_mode,
                prompt=prompt)

        except Exception as e:
            error_message = f"Error processing {file_path}:\n{traceback.format_exc()}"
            errors.append(error_message)
            failed_count += 1

        display_status(args.model, os.path.basename(file_path), 
                       f"{processed_count}/{total_files}", failed_count, errors, last_output)

        if args.delay > 0:
            time.sleep(args.delay)

if __name__ == '__main__':
    main()
