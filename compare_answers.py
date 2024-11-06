import csv
import sys
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

def compare_answers(data, correct_answers, question_stats, bias_stats, global_bias, detailed_stats, failed_paper, skipped_invalid_format, skipped_no_answer_in_csv):
    """Compare answers from the JSON file with the correct answers from the CSV and record bias."""

    matches = 0
    total_comparisons = 0
    skipped_format = 0  # Counter for answers skipped due to invalid format
    skipped_no_csv = 0  # Counter for valid format answers skipped due to no CSV entry

    study_number = clean_study_number(data['PDF_Name'])  # Clean the JSON study number
    valid_comparisons = False  # Track if any comparisons were made for this paper

    for response in data['Prompts']:
        prompt_number = str(response['number'])  # Convert prompt number to string for comparison
        json_answer = parse_json_answer(response['answer'])

        # Check if the answer in the JSON is valid (Yes/No)
        if json_answer is None:
            skipped_format += 1  # Invalid format
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
    return matches, total_comparisons, skipped_format, skipped_no_csv



def prompt_info(prompt_number, question_stats, bias_stats, detailed_stats):
    """Print detailed information for a specific prompt number."""
    if prompt_number in question_stats:
        total_comparisons = question_stats[prompt_number]['total']
        matches = question_stats[prompt_number]['matches']
        accuracy = (matches / total_comparisons) * 100 if total_comparisons > 0 else 0

        # Bias stats
        yes_to_no = bias_stats[prompt_number]['yes_to_no']
        no_to_yes = bias_stats[prompt_number]['no_to_yes']

        # Detailed lists of studies with biases
        yes_to_no_studies = detailed_stats[prompt_number]['yes_to_no']
        no_to_yes_studies = detailed_stats[prompt_number]['no_to_yes']

        print(f"\nDetails for Prompt {prompt_number}:")
        print(f"Total Comparisons: {total_comparisons}")
        print(f"Accuracy (Match Percentage): {accuracy:.2f}% ({matches}/{total_comparisons} matches)")
        print(f"Bias - No instead of Yes: {yes_to_no}, Yes instead of No: {no_to_yes}")
        print(f"Studies where 'No' was answered instead of 'Yes': {', '.join(yes_to_no_studies) if yes_to_no_studies else 'None'}")
        print(f"Studies where 'Yes' was answered instead of 'No': {', '.join(no_to_yes_studies) if no_to_yes_studies else 'None'}")
    else:
        print(f"\nNo data available for Prompt {prompt_number}.")

def main():
    if len(sys.argv) < 3:
        print("Usage: python compare_answers.py <csv_file> <json_file_pattern> [--prompt <prompt_number>]")
        sys.exit(1)

    csv_file = sys.argv[1]
    file_pattern = sys.argv[2]  # Globbing pattern for JSON files
    prompt_number = None

    if '--prompt' in sys.argv:
        prompt_index = sys.argv.index('--prompt') + 1
        if prompt_index < len(sys.argv):
            prompt_number = sys.argv[prompt_index]
        else:
            print("Error: You must specify a prompt number after --prompt.")
            sys.exit(1)

    combine7abc = False
    if '--combine7abc' in sys.argv:
        combine7abc = True

    # Load correct answers from the CSV file
    correct_answers = load_correct_answers(csv_file)

    data = evaluate_all_raw_jsons(file_pattern, combine7abc)

    if not data:
        print(f"No files found for pattern: {file_pattern}")
        sys.exit(1)

    global_matches = 0
    global_total_comparisons = 0
    skipped_invalid_format = 0  # Counter for invalid format answers
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
    for entry in data:

        matches, total_comparisons, skipped_format, skipped_no_csv = compare_answers(
            entry, correct_answers, question_stats, bias_stats, global_bias, detailed_stats, failed_paper, skipped_invalid_format, skipped_no_answer_in_csv
        )

        # Accumulate skipped invalid format and missing CSV answers
        skipped_invalid_format += skipped_format
        skipped_no_answer_in_csv += skipped_no_csv

        if total_comparisons > 0:
            match_percentage = (matches / total_comparisons) * 100
            print(f"File: {entry['PDF_Name']} - Match Percentage: {match_percentage:.2f}% ({matches}/{total_comparisons} matches)")
        else:
            print(f"File: {entry['PDF_Name']} - No valid comparisons")

        global_matches += matches
        global_total_comparisons += total_comparisons

    # If a specific prompt number was provided, display its details
    if prompt_number:
        prompt_info(prompt_number, question_stats, bias_stats, detailed_stats)
        return

    # Calculate and print global match percentage
    if global_total_comparisons > 0:
        global_match_percentage = (global_matches / global_total_comparisons) * 100
        print(f"\nGlobal Match Percentage: {global_match_percentage:.2f}% ({global_matches}/{global_total_comparisons} matches)")
    else:
        print("\nNo valid comparisons across all files.")

    # Print statistics for skipped answers
    print(f"\nSkipped Answers Due to Invalid Format: {skipped_invalid_format}")
    print(f"Skipped Answers Due to Missing CSV Entry: {skipped_no_answer_in_csv}")

    # Print question-based statistics
    print("\nQuestion-Based Statistics:")

    # Sort the keys (prompt numbers) lexicographically to handle alphanumeric values like '7a'
    for question, stats in sorted(question_stats.items(), key=lambda x: (str(x[0]))):
        if stats['total'] > 0:
            question_match_percentage = (stats['matches'] / stats['total']) * 100
            print(f"Question {question}: {question_match_percentage:.2f}% ({stats['matches']}/{stats['total']} matches)")
        else:
            print(f"Question {question}: No valid comparisons")

    # Print question-based bias statistics
    print("\nQuestion-Based Bias Statistics:")

    for question, bias in sorted(bias_stats.items(), key=lambda x: (str(x[0]))):
        yes_to_no = bias['yes_to_no']
        no_to_yes = bias['no_to_yes']

        print(f"Question {question}: No instead of Yes: {yes_to_no}, Yes instead of No: {no_to_yes}")

    # Print global bias statistics
    print("\nGlobal Bias Statistics:")
    print(f"No instead of Yes: {global_bias['yes_to_no']},  Yes instead of No: {global_bias['no_to_yes']}")

    # Print list of failed papers
    if failed_paper:
        print("\nFailed Papers (no valid comparisons):")
        print(", ".join(failed_paper))

if __name__ == '__main__':
    main()
