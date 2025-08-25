# Study-Evaluation-Pipeline

A streamlined pipeline that uploads PDFs to Gemini/OpenAI, where language models analyze and evaluate the content. Responses are automatically compared and saved in a CSV format for further analysis.

## Setup Instructions

### Prerequisites
- Python 3.12 is required for this project.

### Installation Steps
1. **Clone the Repository**  
   ```bash
   git clone https://github.com/Benjino16/Study-Evaluation-Pipeline.git
   cd Study-Evaluation-Pipeline
   ```

2. **(Optional) Check Python Version**  
   ```bash
   python --version  # should match requires-python in pyproject (e.g. 3.10+)
   ```

3. **Create & Activate Virtual Environment**  
   ```bash
   python -m venv .venv
   .\.venv\Scripts\Activate.ps1         # Windows PowerShell
   # source .venv/bin/activate          # macOS/Linux
   ```

4. **Update Build Tools**  
   ```bash
   python -m pip install -U pip wheel setuptools
   ```

5. **Install Project in Development Mode**  
   ```bash
   pip install -e .
   ```

6. **Configure API Keys**  
   Create a `.env` file in the project root:
   ```dotenv
   API_GPT=your_openai_api_key
   API_GEMINI=your_gemini_api_key
   ```
   > An example .env can be found at [`.env.example`](.env.example)

7. **Verify Setup**  
   ```bash
   # via console command (if script entry is defined)
   sep-api-test

   # alternatively as module
   python -m sep.api_request.api_test
   ```


### Commands  
**Note:** Ensure that your API limits are checked, as processing large volumes may impact usage quotas on Gemini/OpenAI.

After installation you can run commands like:

- sep-run
- sep-compare-answers
- sep-create-csv
- sep-combine-csv-answers
- sep-edit-run-information
- sep-evaluate-reconciliation
- sep-export-results
- sep-set-attribute-of-run
- sep-reconcile
- sep-api-test

1. **Start Run**  
   ```bash
   sep-run --model <string> [--files <path>] [--delay <integer>] [--temp <float>] [--process_all] [--pdf_reader]
   ```  
   **Required**  
   `--model` the name of the model (supported models are listed in main.py)  

   **Optional**  
   `--files` the path to the PDF files (supports globbing)  
   `--delay` delay in seconds to wait between API requests  
   `--temp` the temperature of the model (not all models support all temperatures)  
   `--single_process` use this flag if all prompts should be put into splitted API request  
   `--pdf_reader` this flag enables the local PDF reader. Only the text of the PDF will be passed to the API in the model's content window.  

2. **Evaluate Answers**  
   ```bash
   sep-compare-answers --data <string> [--csv <string>] [--include_na]
   ```
   **Required**  
   `--data` the run data (stored in '../Data/Results')  

   **Optional**  
   `--csv` the path to the CSV with the correct answers  
   `--include_na` include NA answers  
   
3. **Export Data**  
   ```bash
   sep-create-csv (--run <string> | --dir <string>) --name <string> --csv <string> [--validation]
   ```
   **Required**  
   `--run` A path to a specific run from which the csv should be created  
   `--dir` A path to a run folder from where the csv is created with all runs.  
   `--name` The name of the exported csv.  
   `--csv` The path of the correct answer csv.  


   **Optional**  
   `--validation` marks the run as a validation run  
   

### Example of using the pipeline
The following example shows how the pipeline can be used. The prerequisite for this is a gemini api key and papers saved as pdf, for which there is already a human evaluation as csv.

1. **Start a run**  
   ```bash
   sep-run --model gemini-1.5-pro --files "papers/*.pdf" --delay 30 --temp 0.8
   ```  
   It will show an overview of the used model, estimated time and a few other informations. Press `Enter Key` to start the run.  
   During the run, you can see the responses of the LLM, possible errors of the API and the progress. After each API call, the data is saved in the configurieten folder (default: “../Data/Results”).

2. **Evaluate data from the run**  
   To evaluate the data after the run, you can use the following command to compare it with the correct answers that have already been saved.
   ```bash
   sep-compare-answers --csv ".\resources\csv\correct_answers.CSV" --data ".\data\output\runs\raw-*.json"
   ``` 
   An overview of the run with statistics is now displayed. The accuracy of the run can also be seen there.

3. **Export data as csv**
   ```bash
   sep-create-csv --run ".\data\output\runs\raw-*.json" --name "exported_data.csv" --csv ".\resources\csv\correct_answers.CSV" --number 1
   ``` 
   This will export the data of the run as csv and additionally append the correct answers.
