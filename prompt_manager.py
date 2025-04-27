import env_manager
import json

# load prompts once at the start
with open(env_manager.PROMPT_PATH, "r", encoding="utf-8") as file:
    _prompt_data = json.load(file)

_system_prompt = _prompt_data["system_prompt"]
_closing_prompt = _prompt_data["closing_prompt"]
_prompts = _prompt_data["prompts"]

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