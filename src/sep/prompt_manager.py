"""
Prompt Manager Module

This module loads prompts from a JSON file and provides functions to retrieve 
individual prompts, all prompts combined, and the total number of prompts.
"""

from sep import env_manager
import json

# Load prompts once at the start


def getPrompt(json_path: str):
    """
    Returns prompts combined with system and closing prompts.
    If index is provided, returns a single prompt wrapped with system and closing prompts.
    
    Raises:
        IndexError: If the index is out of bounds.
    """
    with open(json_path, "r", encoding="utf-8") as file:
        prompt_data = json.load(file)

    return prompt_data["prompt"]

if __name__ == "__main__":
    print(getPrompt())