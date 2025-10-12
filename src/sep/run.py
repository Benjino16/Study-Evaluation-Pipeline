"""
This script provides a command-line interface for processing PDF files with a specified model.
"""

from sep.env_manager import PDF_FOLDER
from sep.prompt_manager import getPromptsLength, getPrompt
from sep.process_paper import process_paper

import argparse
import glob
import os
import time
import datetime
import traceback

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
    parser.add_argument('--files', nargs='+', help='Files or patterns to process (supports globbing).')
    parser.add_argument('--delay', type=int, default=15, help='Delay time in seconds between processing files.')
    parser.add_argument('--temp', type=float, default=1.0, help='The temperature setting for model randomness.')
    parser.add_argument('--single_process', action='store_true', help='Process all prompts in splitted request if set. If --pdf_reader is enabled, it processes each page separately.')
    parser.add_argument('--pdf_reader', action='store_true', help='Uses a local PDF reader to extract content as context for the model.')

    args = parser.parse_args()

    pdf_path = args.files or [PDF_FOLDER + "*.pdf"]
    
    files_to_process = []
    for file_pattern in pdf_path:
        files_to_process.extend(glob.glob(file_pattern))

    files_to_process = list(set(files_to_process))  # Remove duplicate files

    # Show processing overview
    display_overview(args.model, files_to_process, args.delay, not args.single_process, args.temp)
    user_input = input("Press Enter to continue...")
    if user_input != "":
        raise ValueError("Exiting program, user pressed a key other than Enter.")

    total_files = len(files_to_process)
    processed_count = 0
    failed_count = 0
    errors = []

    full_prompt = getPrompt()
    if not full_prompt:
        raise ValueError("Failed to load prompt.")

    # Process each file
    for file_path in files_to_process:
        processed_count += 1
        last_output = None

        try:
            last_output, save_folder = process_paper(full_prompt, args.model, file_path, args.delay, args.temp, args.single_process, args.pdf_reader)
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
