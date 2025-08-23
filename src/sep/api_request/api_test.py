from .gemini_pipeline import test_gemini_pipeline
from .gpt_pipeline import test_gpt_pipeline
from .ollama_pipeline import test_ollama_pipeline
from .gpt_text_pipeline import test_deepseek_pipeline
import logging

logging.basicConfig(level=logging.INFO)

def api_test():
    """
    Sends a test request to the various APIs to see if the service is available.
    """
    logging.info("---- API Test ----")

    logging.info("testing gpt api...")
    gpt_pipeline = test_gpt_pipeline()
    log_test_result(gpt_pipeline)

    logging.info("testing gemini api...")
    gemini_pipeline = test_gemini_pipeline() 
    log_test_result(gemini_pipeline)

    logging.info("testing deepseek api...")
    deepseek_pipeline = test_deepseek_pipeline() 
    log_test_result(deepseek_pipeline)

    logging.info("testing ollama api...")
    ollama_pipeline = test_ollama_pipeline() 
    log_test_result(ollama_pipeline)
    
    return {
        "gpt": gpt_pipeline,
        "gemini": gemini_pipeline,
        "deepseek": deepseek_pipeline,
        "ollama": ollama_pipeline,
        "local": False
    }

def log_test_result(passed: bool):
    logging.info("passed ✅" if passed else "error ❌")

if __name__ == '__main__':
    api_test()