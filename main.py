from env_manager import getPromptsLength
from get_model_name import get_full_model_name
from pipeline_manager import run_request
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
VALID_MODELS = ['gpt-4o', 'gpt-4o-mini', 'gpt-4-turbo', 'gemini-2.0-flash-exp', 'gemini-1.5-pro', 
                'gemini-1.0-pro', 'gemini-1.5-flash', 'o1-preview', 'deepseek-r1:32b', 'deepseek-chat', 'gemini-2.0-pro-exp-02-05', 'gemini-1.5-pro-latest', 'gemini-2.5-pro-exp-03-25']

def clear_console():
    os.system('cls' if os.name == 'nt' else 'clear')

def display_overview(model: str, files_to_process, delay: int, process_all: bool, temperature: float):
    clear_console()
    if process_all:
        time_calculation = (delay + 5) * len(files_to_process)
    else:
        time_calculation = (delay + 5) * len(files_to_process) * getPromptsLength()

    formatted_time = str(datetime.timedelta(seconds=time_calculation))

    print("\n-------- overview --------\n")
    print(f"model: {model}")
    print(f"temperature: {temperature}")
    print(f"files: {files_to_process}")
    print(f"delay between requests: {delay}")
    print(f"process all prompts: {process_all}")
    print(f"Calculated Time: {formatted_time}")

def display_status(model, current_file, progress, failed, errors, last_output):
    clear_console()
    print(f"model: {model}")
    print(f"paper: {current_file}")
    print(f"progress: {progress}")
    print(f"failed: {failed}\n")
    
    print("\n-------- last answer --------\n")
    print(last_output or "Waiting for output...")
    
    if errors:
        print("\n-------- errors --------\n")
        for error in errors:
            print(error)
            
    print("\n-------- live protocol --------\n")

def main():
    parser = argparse.ArgumentParser(description='Process files with specified model (gpt or gemini).')
    parser.add_argument('--model', required=True, help='Model to use (e.g., gpt-4o, gemini-3).')
    parser.add_argument('--files', nargs='+', required=True, help='Files or patterns to process (supports globbing).')
    parser.add_argument('--delay', type=int, default=15, help='Delay time in seconds between processing files.')
    parser.add_argument('--temp', type=float, default=1.0, help='The temperature of the model.')
    parser.add_argument('--process_all', action='store_true', help='Process all prompts in a single request if set. If --pdf_reader is set, it will process each page seperetly.')
    parser.add_argument('--pdf_reader', action='store_true', help='Uses a local pdf reader and provides the extracted as a context for the model.')

    args = parser.parse_args()

    if args.model not in VALID_MODELS:
        print(f"Error: Invalid model '{args.model}' specified. Supported models are: {', '.join(VALID_MODELS)}")
        sys.exit(1)

    files_to_process = []
    for file_pattern in args.files:
        files_to_process.extend(glob.glob(file_pattern))

    files_to_process = list(set(files_to_process))  # remove double files

    #get exact model information
    try:
        full_model_name = get_full_model_name(args.model)
    except Exception as e:
        error_message = f"Error retrieving model information:\n{traceback.format_exc()}"
        print(error_message)
        exit()

    #get pdf reader version
    if args.pdf_reader:
        pdf_reader_version = get_pdf_reader_version()
    else:
        pdf_reader_version = '-'

    #get process mode
    if args.process_all:
        process_mode = "process full pdf in single request"
    else:
        process_mode = "process full pdf with prompt splitted request"

    display_overview(full_model_name, files_to_process, args.delay, args.process_all, args.temp)
    eingabe = input("Drücke Enter, um fortzufahren...")
    if eingabe != "":
        print("Programm wird abgebrochen.")
        exit()

    total_files = len(files_to_process)
    processed_count = 0
    failed_count = 0
    errors = []

    
    

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
            last_output, prompt = run_request(file_path, args.model, args.process_all, args.pdf_reader, args.delay, args.temp)
                
            if last_output is None:
                raise(f"Skipping evaluation for {file_path} due to processing error.")
            
            save_raw_data_as_json(
                raw_data=last_output, 
                pdf_name=os.path.basename(file_path), 
                model_name=full_model_name,
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
