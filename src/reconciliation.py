"""
This script performs reconciliation between the outputs of two LLMs (Large Language Models) based on mismatches in their answers.
It uses questions, answers, and PDFs as context to evaluate and identify mistakes.
"""

import time
from src.api_request.request_manager import run_prompt
from env_manager import getQuestion, getPDFPath
from save_raw_data import save_raw_data_as_json
import logging

logging.basicConfig(level=logging.INFO)

def run_reconciliation(mismatches, model1: str, model2: str, delay: int):
    """
    Run reconciliation process for all studies with mismatches.
    """
    for study in mismatches:
        study_number = study['study_number']
        data = study['mismatches']
        logging.info(f"Reconciliation for Study: {study_number}")
        result = reconciliate(data, study_number, model1, model2)
        # Save raw data if needed
        #!!save_raw_data_as_json(result, study_number, model1)
        # NOT SAVED
        logging.info(f"Result: {result}")
        if delay > 0:
            time.sleep(delay)

def reconciliate(data, filename: str, model1: str, model2: str):
    """
    Create a prompt to identify mistakes based on mismatches and run it through a language model.

    Returns:
        dict: Reconciliation result containing identified mistakes.
    """
    # Context: questions + errors + PDF
    system = (
        "Answer in JSON format. Make a list of all the numbers where you made mistakes. "
        "Below you will find a list of answers that you submitted based on the PDF. "
        "Another LLM has come to different conclusions. Check the evidence of the other model "
        "and if you come to the conclusion that you have made a mistake in your own answer, then "
        "add the number of the question to the JSON list together with a reason. "
        "Format: {'mistakes': [ { number: int, reason: string } ]}"
    )
    modelText1 = "You are 'model1', the other LLM is 'model2'!"
    modelText2 = "You are 'model2', the other LLM is 'model1'!"
    
    questions = getAllQuestions(data)
    prompt = f"[Prompt]{system}\n[Questions]\n{questions}\n{modelText1}\n[Answers]{data}"
    filepath = getPDFPath(filename)

    return run_prompt(prompt, filepath, model1, False, 0.2)

def getAllQuestions(data):
    """
    Retrieve all questions related to the given mismatch data.

    Returns:
        list: List of retrieved questions.
    """
    questionList = []
    for entry in data:
        number = entry['number']
        try:
            number_int = int(number)
            if number_int > 7:
                number_int += 2
        except ValueError:
            if number == '7a':
                number_int = 7
            if number == '7b':
                number_int = 8
            if number == '7c':
                number_int = 9
        number_int -= 1
        questionList.append({getQuestion(int(number_int))})
    return questionList
