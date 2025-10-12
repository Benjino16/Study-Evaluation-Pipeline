from sep.utils.load_json import load_json
from sep.api_request.gemini_pipeline import process_file_with_gemini
import sys

PATH_TO_PROMPT_DESIGNER = r"D:\dev\github\Study-Evaluation-Pipeline\resources\prompt_designer.json"

def adjust_prompt(old_prompt: str, paper: str) -> str:
    """This method adjusts a given prompt based on the paper's content."""
    prompt_dict = load_json(PATH_TO_PROMPT_DESIGNER)
    prompt_designer_prompt = prompt_dict["prompt"]
    new_prompt = process_file_with_gemini(prompt_designer_prompt + "Prompt: " + old_prompt, paper, "gemini-2.5-pro", 1.0)
    return new_prompt


test = f"""
1. Is an investigated human population appropriately reported? 
2. Is an investigated animal population appropriately reported?  
3. Is a cell line experiment appropriately reported? 
4. Does the paper name an intervention?
5. Does the paper state a hypothesis?
6. Does the paper identify a primary outcome?
7a. Is the statistical test reported?
7b. Is the test statistics reported? 
7c. Are statistical decision criteria properly reported?
8. Did the authors acknowledge any limitations or biases?
9. Did the authors explicitly state inclusion criteria?
10. Did the authors explicitly state exclusion criteria? 
11. Are experimental units randomised?
12. Does the paper explicitly state the exact sample size? 
"""



if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python script.py <id>")
        sys.exit(1)

    test_id = sys.argv[1]
    prompt = adjust_prompt(test, test_id)
    print(prompt)
