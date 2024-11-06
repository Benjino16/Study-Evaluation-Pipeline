# Study-Evaluation-Pipeline

A streamlined pipeline that uploads PDFs to Gemini/OpenAI, where language models analyze and evaluate the content. Responses are automatically compared and saved in a CSV format for further analysis.

## Setup Instructions

### Prerequisites
- Python 3.12 is required for this project.

### Installation Steps
1. **Clone the Repository**  
   Clone this repository to your local machine.
   
   ```bash
   git clone https://github.com/yourusername/Study-Evaluation-Pipeline.git
   cd Study-Evaluation-Pipeline
   ```

2. **Install Requirements**  
   Install all dependencies listed in `requirements.txt`.
   
   ```bash
   pip install -r requirements.txt
   ```

3. **Configure API Keys**  
   Create a `secrets.env` file in the root directory of the project. This file should contain your API keys for Gemini and OpenAI, formatted as follows:

   ```plaintext
   API_GPT=your_openai_api_key
   API_GEMINI=your_gemini_api_key
   ```

4. **Run Setup Test**  
   Verify your setup by running the following command. This will check for any issues and confirm that the environment is correctly configured.
   
   ```bash
   python api_test.py
   ```

### Usage
Once setup is complete, you can start the pipeline to upload and evaluate PDFs, then save the responses as CSVs for analysis.

**Note:** Ensure that your API limits are checked, as processing large volumes may impact usage quotas on Gemini/OpenAI.
