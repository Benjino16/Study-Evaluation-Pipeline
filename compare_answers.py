import argparse
import csv
import sys
import re
from collections import defaultdict
from evaluate_raw import evaluate_all_raw_jsons

def clean_study_number(study_number):
    """Clean study number by removing file extensions and leading zeros."""
    study_number = study_number.replace('.pdf', '')  # Remove .pdf if it exists
    study_number = study_number.lstrip('0')  # Remove leading zeros
    return study_number

def load_correct_answers(csv_file):
    """Load correct answers from the CSV file into a dictionary."""
    correct_answers = {}
    with open(csv_file, newline='') as f:
        reader = csv.DictReader(f, delimiter=';')
        for row in reader:
            study_number = clean_study_number(row['study_number'])
            prompt_number = row['prompt_number']
            answer = row['answer']

            # Ignore rows with NA answers
            if answer != "NA":
                correct_answers[(study_number, prompt_number)] = answer
    return correct_answers

def parse_json_answer(answer):
    """Parse the JSON answer into '1' for yes, '0' for no, or None for invalid answers."""
    yes_answers = {"Yes", "yes"}
    no_answers = {"No", "no"}

    if answer in yes_answers:
        return '1'
    elif answer in no_answers:
        return '0'
    else:
        return None  # Invalid answer or "No Answer"

def compare_answers(data, correct_answers, question_stats, bias_stats, global_bias, detailed_stats, failed_paper):
    """Compare answers from the JSON file with the correct answers from the CSV and record bias."""

    matches = 0
    total_comparisons = 0

    skipped_format = 0  # Counter for answers skipped due to invalid format
    skipped_format_list = []

    skipped_no_csv = 0  # Counter for valid format answers skipped due to no CSV entry

    study_number = clean_study_number(data['PDF_Name'])  # Clean the JSON study number
    valid_comparisons = False  # Track if any comparisons were made for this paper

    for response in data['Prompts']:
        prompt_number = str(response['number'])  # Convert prompt number to string for comparison
        json_answer = parse_json_answer(response['answer'])

        # Check if the answer in the JSON is valid (Yes/No)
        if json_answer is None:
            skipped_format += 1  # Invalid format
            skipped_format_list.append(response)
        else:
            # Check if there is a corresponding correct answer in the CSV
            if (study_number, prompt_number) not in correct_answers:
                skipped_no_csv += 1  # Valid format, but missing CSV entry
            else:
                valid_comparisons = True  # Mark that this paper has at least one valid comparison
                correct_answer = correct_answers[(study_number, prompt_number)]
                
                if json_answer == correct_answer:
                    matches += 1
                    question_stats[prompt_number]['matches'] += 1  # Increment question-level matches
                else:
                    # Record the bias direction (per question)
                    if correct_answer == '1' and json_answer == '0':
                        bias_stats[prompt_number]['yes_to_no'] += 1
                        detailed_stats[prompt_number]['yes_to_no'].append(study_number)
                        global_bias['yes_to_no'] += 1  # Increment global yes->no bias
                    elif correct_answer == '0' and json_answer == '1':
                        bias_stats[prompt_number]['no_to_yes'] += 1
                        detailed_stats[prompt_number]['no_to_yes'].append(study_number)
                        global_bias['no_to_yes'] += 1  # Increment global no->yes bias

                question_stats[prompt_number]['total'] += 1  # Increment total for this question
                total_comparisons += 1

    # If no valid comparisons were made for the entire paper, mark it as failed
    if not valid_comparisons:
        failed_paper.append(study_number)

    # Return the count of skipped invalid and missing CSV entries for tracking
    return matches, total_comparisons, skipped_format, skipped_format_list, skipped_no_csv


def main():
    parser = argparse.ArgumentParser(description='Process files with specified model (gpt or gemini).')
    parser.add_argument('--csv', type=str, required=True, help='The csv that the results should be compared to.')
    parser.add_argument('--data', type=str, required=True, help='The json raw data that should be evaluated (supports globbing).')
    parser.add_argument('--combine7abc', action='store_true', help='Combines the answers of 7a, 7b and 7c to one.')

    args = parser.parse_args()

    csv_file = args.csv
    file_pattern = args.data

    combine7abc = args.combine7abc

    # Load correct answers from the CSV file
    correct_answers = load_correct_answers(csv_file)

    data = evaluate_all_raw_jsons(file_pattern, combine7abc)

    if not data:
        print(f"No files found for pattern: {file_pattern}")
        sys.exit(1)

    global_matches = 0
    global_total_comparisons = 0
    skipped_invalid_format = 0  # Counter for invalid format answers
    skipped_list = []
    skipped_no_answer_in_csv = 0  # Counter for missing CSV answers

    failed_paper = []  # List to keep track of papers where all answers were skipped

    # Dictionary to store matches and total comparisons for each question (prompt)
    question_stats = defaultdict(lambda: {'matches': 0, 'total': 0})

    # Dictionary to store bias statistics for each question (prompt)
    bias_stats = defaultdict(lambda: {'yes_to_no': 0, 'no_to_yes': 0})

    # Dictionary to store detailed statistics (study numbers) for each question (prompt)
    detailed_stats = defaultdict(lambda: {'yes_to_no': [], 'no_to_yes': []})


    print(f"\nFile statistics:")
    # Global bias counters
    global_bias = {'yes_to_no': 0, 'no_to_yes': 0}

        # Compare each JSON file with the correct answers
    for entry in data:

        matches, total_comparisons, skipped_format, skipped_format_list, skipped_no_csv = compare_answers(
            entry, correct_answers, question_stats, bias_stats, global_bias, detailed_stats, failed_paper
        )

        # Accumulate skipped invalid format and missing CSV answers
        skipped_invalid_format += skipped_format
        for skipped_entry in skipped_format_list:
            skipped_list.append(f"- File: {entry['PDF_Name']} {skipped_entry}")
        skipped_no_answer_in_csv += skipped_no_csv

        if total_comparisons > 0:
            match_percentage = (matches / total_comparisons) * 100
            print(f"File: {entry['PDF_Name']} - Match Percentage: {match_percentage:.2f}% ({matches}/{total_comparisons} matches)")
        else:
            print(f"File: {entry['PDF_Name']} - No valid comparisons")

        global_matches += matches
        global_total_comparisons += total_comparisons
    

    # Print statistics for skipped answers
    print(f"\n\033[31mError in format:   {skipped_invalid_format}\033[0m" if skipped_invalid_format != 0 else f"\nError in format:   {skipped_invalid_format}")
    print(f"CSV entry missing: {skipped_no_answer_in_csv}")
    if skipped_list:
        print(f"Format Error List:")
        print(* skipped_list, sep='\n')

    def custom_sort_key(question):
        """Sort keys so that numeric parts are sorted numerically and alphabetically for suffixes."""
        match = re.match(r"(\d+)([a-zA-Z]*)", question)
        if match:
            number = int(match.group(1))
            suffix = match.group(2)
            return (number, suffix)
        return (float('inf'), question)  # Put non-matching keys at the end if any

    # Print combined question-based statistics in a formatted single-line per question
    # Define the header with consistent width
    header = f"\n{'Question':<12} {'Match %':>8} {'Matches':<6} | {'Bias (yes/no)':<1}"
    print(header)
    print('-' * len(header))  # Print a line under the header for readability

    # Sort the keys using custom_sort_key
    for question in sorted(question_stats.keys(), key=custom_sort_key):
        stats = question_stats[question]
        bias = bias_stats[question]

        total_comparisons = stats['total']
        matches = stats['matches']
        yes_to_no = bias['yes_to_no']
        no_to_yes = bias['no_to_yes']

        if total_comparisons > 0:
            question_match_percentage = (matches / total_comparisons) * 100
            # Format each line with consistent width for matches and bias
            formatted_line = f"{question:<12} {question_match_percentage:>6.2f}% ({matches:>2}/{total_comparisons:<2}) | {yes_to_no:>2}/{no_to_yes:<2}"
        else:
            # If there are no valid comparisons for the question
            formatted_line = f"{question:<12} No valid comparisons"

        # Print the formatted line for each question
        print(formatted_line)


    # Calculate and print global match percentage
    if global_total_comparisons > 0:
        global_match_percentage = (global_matches / global_total_comparisons) * 100
        print("\nGlobal Match Percentage: ")
        print(f"\033[1;31m{global_match_percentage:.2f}% ({global_matches}/{global_total_comparisons} matches) | Bias: {global_bias['yes_to_no']}/{global_bias['no_to_yes']} (yes/not)\033[0m")
    else:
        print("\nNo valid comparisons across all files.")

    # Print list of failed papers
    if failed_paper:
        print("\nFailed Papers (no valid comparisons):")
        print(", ".join(failed_paper))

if __name__ == '__main__':
    main()
