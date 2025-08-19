"""
Prompt Manager Module

This module loads prompts from a JSON file and provides functions to retrieve 
individual prompts, all prompts combined, and the total number of prompts.
"""

from src import env_manager
import json

# Load prompts once at the start
with open(env_manager.PROMPT_PATH, "r", encoding="utf-8") as file:
    _prompt_data = json.load(file)

_system_prompt = _prompt_data["system_prompt"]
_closing_prompt = _prompt_data["closing_prompt"]
_prompts = _prompt_data["prompts"]

def getQuestion(index: int):
    """
    Returns a single prompt by index.
    
    Raises:
        IndexError: If the index is out of bounds.
    """
    if 0 <= index < len(_prompts):
        return _prompts[index]
    else:
        raise IndexError("Prompt index out of bounds!")

def getPrompt(index=None):
    """
    Returns prompts combined with system and closing prompts.
    If index is provided, returns a single prompt wrapped with system and closing prompts.
    
    Raises:
        IndexError: If the index is out of bounds.
    """
    if index is None:
        return f"{_system_prompt}\n" + "\n".join(_prompts) + f"\n{_closing_prompt}"
    elif 0 <= index < len(_prompts):
        return f"{_system_prompt}\n{_prompts[index]}\n{_closing_prompt}"
    else:
        raise IndexError("Prompt index out of bounds!")

def getPromptsLength():
    """
    Returns the number of available prompts.
    """
    return len(_prompts)
