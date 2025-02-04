from gpt_pipeline import process_pdf_with_openai
from env_manager import getQuestion

def reconciliate(data, filename: str, model1: str, model2: str):
    #Context: questions + errors + pdf
    prompt = "Answer in json format. Make a list of all the numbers where you made mistakes. Below you will find a list of answers that you submitted based on the PDF. Another LLM has come to different conclusions. Check the evidence of the other model and if you come to the conclusion that you have made a mistake in your own answerq, then add the number of the question to the json list."
    questions = getQuestion(1)
    answers = ""
    other_answers = ""


    print(f"{data, questions, answers, other_answers}")