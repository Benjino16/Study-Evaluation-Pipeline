import os
import json
from dotenv import load_dotenv, find_dotenv

prompt_path = "prompts.json"
pdf_path = "../Data/PDFs/"

dotenv_path = find_dotenv('.env')
load_dotenv(dotenv_path)

def env(key):
    return os.getenv(key)

def getQuestion(index: int):
    with open(prompt_path, "r", encoding="utf-8") as file:
        data = json.load(file)

    prompts = data["prompts"]

    if 0 <= index < len(prompts):
        return f"{prompts[index]}"
    else:
        raise Exception("Prompt Index out of bounds!")

def getPrompt(index=None):
    with open(prompt_path, "r", encoding="utf-8") as file:
        data = json.load(file)

    system_prompt = data["system_prompt"]
    closing_prompt = data["closing_prompt"]
    prompts = data["prompts"]

    if index is None:
        return f"{system_prompt}\n" + "\n".join(prompts) + f"\n{closing_prompt}"
    elif 0 <= index < len(prompts):
        return f"{system_prompt}\n{prompts[index]}\n{closing_prompt}"
    else:
        raise Exception("Prompt Index out of bounds!")


def getPromptsLength():
    with open("prompts.json", "r", encoding="utf-8") as file:
        data = json.load(file)

    prompts = data["prompts"]
    return len(prompts)

def getPDFPath(number: str):
    return f"{pdf_path}{number.zfill(4)}.pdf"

if __name__ == '__main__':
    print(getPrompt())
