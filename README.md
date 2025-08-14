# Study-Evaluation-Pipeline

A streamlined pipeline that uploads PDFs to Gemini/OpenAI, where language models analyze and evaluate the content. Responses are automatically compared and saved in a CSV format for further analysis.

## Setup Instructions

### Prerequisites
- Python 3.12 is required for this project.

### Installation Steps
1. **Clone the Repository**  
   Clone this repository to your local machine.
   
   ```bash
   git clone https://github.com/Benjino16/Study-Evaluation-Pipeline.git
   cd Study-Evaluation-Pipeline
   ```

2. **Install Requirements**  
   Install all dependencies listed in `requirements.txt`.
   
   ```bash
   pip install -r requirements.txt
   ```

3. **Configure API Keys**  
   Create a `.env` file in the root directory of the project. This file should contain your API keys for Gemini and OpenAI, formatted as follows:

   ```plaintext
   API_GPT=your_openai_api_key
   API_GEMINI=your_gemini_api_key
   ```

4. **Run Setup Test**  
   Verify your setup by running the following command. This will check for any issues and confirm that the environment is correctly configured.
   
   ```bash
   python api_test.py
   ```


### Commands  
**Note:** Ensure that your API limits are checked, as processing large volumes may impact usage quotas on Gemini/OpenAI.

1. **Start Run**  
   ```bash
   python main.py --model <string> --files <path> --delay <integer> --temp <float> <--process_all> <--pdf_reader>
   ```  
   `--model` the name of the model (supported models are listed in main.py)  
   `--files` the path to the PDF files (supports globbing)  
   `--delay` delay in seconds to wait between API requests  
   `--temp` the temperature of the model (not all models support all temperatures)  
   `--single_process` use this flag if all prompts should be put into splitted API request
   `--pdf_reader` this flag enables the local PDF reader. Only the text of the PDF will be passed to the API in the model's content window.  

2. **Evaluate Answers**  
   ```bash
   python compare_answers.py --csv <string> --data <string>
   ```  
   `--csv` the path to the CSV with the correct answers  
   `--data` the run data (stored in '../Data/Results')  

### Example of using the pipeline
The following example shows how the pipeline can be used. The prerequisite for this is a gemini api key and papers saved as pdf, for which there is already a human evaluation as csv.

1. **Start a run**  
   ```bash
   python main.py --model gemini-1.5-pro --files "papers/*.pdf" --delay 30 --temp 0.8
   ```  
   It will show an overview of the used model, estimated time and a few other informations. Press `Enter Key` to start the run.  
   During the run, you can see the responses of the LLM, possible errors of the API and the progress. After each API call, the data is saved in the configurieten folder (default: “../Data/Results”).

2. **Evaluate data from the run**  
   To evaluate the data after the run, you can use the following command to compare it with the correct answers that have already been saved.
   ```bash
   python compare_answers.py --csv "correct_answers.CSV" --data "../Data/Results/raw-*.json"
   ``` 
   An overview of the run with statistics is now displayed. The accuracy of the run can also be seen there.

3. **Export data as csv**
   ```bash
   python create_csv.py --run "../Data/Results/raw-*.json" --name "exported_data.csv" --csv "correct_answers.CSV" --number 1
   ``` 
   This will export the data of the run as csv and additionally append the correct answers.