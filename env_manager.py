import os
import json
from dotenv import load_dotenv, find_dotenv

prompt_path = "prompts.json"
pdf_path = "../Data/PDFs/"

dotenv_path = find_dotenv('.env')
load_dotenv(dotenv_path)

# load prompts once at the start
with open(prompt_path, "r", encoding="utf-8") as file:
    _prompt_data = json.load(file)

_system_prompt = _prompt_data["system_prompt"]
_closing_prompt = _prompt_data["closing_prompt"]
_prompts = _prompt_data["prompts"]

def env(key):
    return os.getenv(key)

def getQuestion(index: int):
    if 0 <= index < len(_prompts):
        return _prompts[index]
    else:
        raise IndexError("Prompt Index out of bounds!")

def getPrompt(index=None):
    if index is None:
        return f"{_system_prompt}\n" + "\n".join(_prompts) + f"\n{_closing_prompt}"
    elif 0 <= index < len(_prompts):
        return f"{_system_prompt}\n{_prompts[index]}\n{_closing_prompt}"
    else:
        raise IndexError("Prompt Index out of bounds!")

def getPromptsLength():
    return len(_prompts)

def getPDFPath(number: str):
    return f"{pdf_path}{number.zfill(4)}.pdf"

if __name__ == '__main__':
    print(getPrompt(13))