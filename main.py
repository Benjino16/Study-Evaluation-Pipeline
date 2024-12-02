from gemini_pipeline import process_file_with_gemini
from gpt_pipeline import process_pdf_with_openai
from gpt_text_pipeline import process_text_with_openai
from save_raw_data import save_raw_data_as_json

import argparse
import glob
import os
import time
import sys

# Supported Models
VALID_MODELS = ['gpt-4o', 'gpt-4o-mini', 'gpt-4-turbo', 'gemini-1.5-pro', 
                'gemini-1.0-pro', 'gemini-1.5-flash', 'o1-preview']

def clear_console():
    os.system('cls' if os.name == 'nt' else 'clear')

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
    parser.add_argument('--delay', type=int, default=0, help='Delay time in seconds between processing files.')
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
            if args.model.lower().startswith('gemini'):
                if args.pdf_reader:
                    exit("Für gemini Modelle gibt es noch keine PDF-Reader option.")
                last_output = process_file_with_gemini(
                    file_path, model=args.model, process_all=args.process_all, delay=args.delay
                )
            elif args.model.lower().startswith('gpt'):
                if args.pdf_reader:
                    last_output = process_text_with_openai(
                        file_path, model=args.model, process_all=True, delay=args.delay
                    )
                else:
                    last_output = process_pdf_with_openai(
                        file_path, model=args.model, process_all=args.process_all, delay=args.delay
                    )
            elif args.model.lower().startswith('o1'):
                if args.pdf_reader:
                    last_output = process_text_with_openai(
                        file_path, model=args.model, process_all=True, delay=args.delay
                    )
                else:
                    exit("Eine Anfrage an ein o1 Modell ist ohne PDF-Reader nicht möglich.")

                
            if last_output is None:
                error_message = f"Skipping evaluation for {file_path} due to processing error."
                errors.append(error_message)
                failed_count += 1
            else:
                save_raw_data_as_json(last_output, os.path.basename(file_path), args.model)

        except Exception as e:
            error_message = f"Error processing {file_path}: {str(e)}"
            errors.append(error_message)
            failed_count += 1

        display_status(args.model, os.path.basename(file_path), 
                       f"{processed_count}/{total_files}", failed_count, errors, last_output)

        if args.delay > 0:
            time.sleep(args.delay)

if __name__ == '__main__':
    main()
