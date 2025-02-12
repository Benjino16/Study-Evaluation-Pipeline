import time
from pipeline_manager import run_prompt
from env_manager import getQuestion, getPDFPath
from save_raw_data import save_reconciliation_as_json


def run_reconciliation(mismatches, model1: str, model2: str, delay: int):
    for study in mismatches:
        study_number = study['study_number']
        data = study['mismatches']
        print(f"Reconciliation for Study: {study_number}")
        result = reconciliate(data, study_number, model1, model2)
        save_reconciliation_as_json(result, study_number, model1)
        print(f"Result: {result}")
        if delay > 0:
            time.sleep(delay)

def reconciliate(data, filename: str, model1: str, model2: str):
    #Context: questions + errors + pdf
    system = "Answer in json format. Make a list of all the numbers where you made mistakes. Below you will find a list of answers that you submitted based on the PDF. Another LLM has come to different conclusions. Check the evidence of the other model and if you come to the conclusion that you have made a mistake in your own answer, then add the number of the question to the json list. Json: {'mistakes': [ numbers ]}"
    modelText1 = "You are 'model1' the other LLM is 'model2'!"
    modelText2 = "You are 'model2' the other LLM is 'model1'!"
    
    questions = getAllQuestions(data)
    prompt = f"[Prompt]{system}\n[Questions]\n{questions}\n{modelText1}\n[Answers]{data}"
    filepath = getPDFPath(filename)

    return run_prompt(prompt, filepath, model1, False, 1.0)


def getAllQuestions(data):
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