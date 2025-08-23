import argparse
import csv
import sys
import re
from collections import defaultdict
from sep.evaluation.load_saved_json import load_saved_jsons
from sep.evaluation.evaluation import clean_study_number
from sep.evaluation.evaluation import parse_json_answer
from sep.env_manager import DEFAULT_CSV
import logging

"""This script can be used to evaluate saved responses from the AI models."""


logging.basicConfig(level=logging.INFO)

# Papers that should be in the run
papers = [
    "0005", "0013", "0019", "0031", "0054", "0094", "0098", "0100", "0110", "0124", "0125", "0129", "0172",
    "0191", "0214", "0223", "0226", "0280", "0317", "0379", "0400", "0424", "0435", "0480", "0491", "0535",
    "0541", "0646", "0665", "0705", "0714", "0732", "0760", "0819", "0827", "0837", "0887", "0891", "0935"
]

def load_correct_answers(csv_file, ignore_na: bool = False):
    """Load correct answers from the CSV file into a dictionary."""
    correct_answers = {}
    with open(csv_file, newline='') as f:
        reader = csv.DictReader(f, delimiter=';')
        for row in reader:
            study_number = clean_study_number(row['study_number'])
            prompt_number = row['prompt_number']
            answer = row['answer']

            if ignore_na and answer == "NA":
                continue
            correct_answers[(study_number, prompt_number)] = answer
    return correct_answers

def load_human_answers(csv_file, ignore_na: bool = False):
    """Load human answers from the CSV file into a dictionary."""
    correct_answers = {}
    with open(csv_file, newline='') as f:
        reader = csv.DictReader(f, delimiter=';')
        for row in reader:
            study_number = clean_study_number(row['study_number'])
            prompt_number = row['prompt_number']
            answer1 = row['run1']
            answer2 = row['run2']

            if ignore_na and (answer1 == "NA" or answer2 == "NA"):
                continue
            correct_answers[(study_number, prompt_number)] = answer1, answer2
    return correct_answers

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

def run_comparison(csv: str, filepath: str, combine7abc: bool, ignore_na: bool = False):
    data = load_saved_jsons(filepath, combine7abc)
    if not data:
        raise ValueError(f"No files found for pattern: {filepath}")
    return compare_data(data, csv, ignore_na)

def compare_data(data, csv: str, ignore_na: bool = False):
    """
    Compares the data from a run with the answers from a CSV file.
    data: the extracted data from a run
    csv: a path of the csv

    returns: a dictionary with usefull information of the comparison
    """
    csv_file = csv
    # Load correct answers from the CSV file
    correct_answers = load_correct_answers(csv_file, ignore_na)

    required_files = []
    required_files.extend(papers)

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

    
    # Global bias counters
    global_bias = {'yes_to_no': 0, 'no_to_yes': 0}

        # Compare each JSON file with the correct answers
    # List to store results for sorting
    results = []

    # Original loop for processing data entries
    for entry in data:
        matches, total_comparisons, skipped_format, skipped_format_list, skipped_no_csv = compare_answers(
            entry, correct_answers, question_stats, bias_stats, global_bias, detailed_stats, failed_paper
        )

        try:
            required_files.remove(entry['PDF_Name'])
        except:
            logging.warning(entry['PDF_Name'] + " could not be removed from required_files. If you are using a different paper set, ignore this warning.")

        # Accumulate skipped invalid format and missing CSV answers
        skipped_invalid_format += skipped_format
        for skipped_entry in skipped_format_list:
            skipped_list.append(f"- File: {entry['PDF_Name']} {skipped_entry}")
        skipped_no_answer_in_csv += skipped_no_csv

        if total_comparisons > 0:
            match_percentage = (matches / total_comparisons) * 100
            # Save result to list for later sorting
            results.append({
                'PDF_Name': entry['PDF_Name'],
                'match_percentage': match_percentage,
                'matches': matches,
                'total_comparisons': total_comparisons
            })
        else:
            # Save result indicating no valid comparisons
            results.append({
                'PDF_Name': entry['PDF_Name'],
                'match_percentage': None,
                'matches': matches,
                'total_comparisons': total_comparisons
            })

        global_matches += matches
        global_total_comparisons += total_comparisons

    # Sort results by match_percentage (putting entries with None at the end)
    sorted_results = sorted(
        results,
        key=lambda x: x['match_percentage'] if x['match_percentage'] is not None else -1,
        reverse=True
    )

    result = {
        'pdf_stats': sorted_results,
        'question_stats': question_stats,

        'bias_stats': bias_stats,
        'global_bias': global_bias,
        'global_matches': global_matches,
        'global_total_comparisons': global_total_comparisons,

        'skipped_no_answer_in_csv': skipped_no_answer_in_csv,
        'skipped_list': skipped_list,
        'skipped_invalid_format': skipped_invalid_format,
        'failed_paper': failed_paper,
        'missing_paper': required_files
    }
    return result

def print_result(result):
    """
    Outputs the information from compare_data().
    result: should be the data that is returned from compare_data()
    """

    sorted_results = result['pdf_stats']
    question_stats = result['question_stats']
    global_bias = result['global_bias']
    global_matches = result['global_matches']
    global_total_comparisons = result['global_total_comparisons']
    bias_stats = result['bias_stats']
    skipped_no_answer_in_csv = result['skipped_no_answer_in_csv']
    skipped_list = result['skipped_list']
    skipped_invalid_format = result['skipped_invalid_format']
    failed_paper = result['failed_paper']
    missing_paper = result['missing_paper']

    # Print the sorted results
    for result in sorted_results:
        if result['match_percentage'] is not None:
            print(f"File: {result['PDF_Name']} - Match Percentage: {result['match_percentage']:.2f}% ({result['matches']}/{result['total_comparisons']} matches)")
        else:
            print(f"File: {result['PDF_Name']} - No valid comparisons")

    

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
    if missing_paper:
        print("\nMissing Papers (no run):")
        print(", ".join(missing_paper))

def main():
    parser = argparse.ArgumentParser(description='Process files with specified model (gpt or gemini).')
    parser.add_argument('--data', type=str, required=True, help='The json raw data that should be evaluated (supports globbing).')
    parser.add_argument('--csv', type=str, help='The csv that the results should be compared to.')
    parser.add_argument('--combine7abc', action='store_true', help='Combines the answers of 7a, 7b and 7c to one.')
    parser.add_argument('--include_na', action='store_false', help='Ignores the NA answers, both of the model an the correct answers.')

    args = parser.parse_args()

    csv = args.csv or DEFAULT_CSV
    ignore_na = args.include_na

    result = run_comparison(csv, args.data, args.combine7abc, ignore_na)
    print_result(result)


if __name__ == '__main__':
    main()