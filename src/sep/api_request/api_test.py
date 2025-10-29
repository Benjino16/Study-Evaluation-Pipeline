from .gemini import test_gemini_pipeline
from .gpt import test_gpt_pipeline
from .deepseek import test_deepseek_pipeline
from sep.logger import setup_logger

log = setup_logger(__name__)

def api_test():
    """
    Sends a test request to the various APIs to see if the service is available.
    """
    log.info("---- API Test ----")

    log.info("testing gpt api...")
    gpt_pipeline = test_gpt_pipeline()
    log_test_result(gpt_pipeline)

    log.info("testing gemini api...")
    gemini_pipeline = test_gemini_pipeline() 
    log_test_result(gemini_pipeline)

    log.info("testing deepseek api...")
    deepseek_pipeline = test_deepseek_pipeline() 
    log_test_result(deepseek_pipeline)

    
    return {
        "gpt": gpt_pipeline,
        "gemini": gemini_pipeline,
        "deepseek": deepseek_pipeline,
        "local": False
    }

def log_test_result(passed: bool):
    log.info("passed ✅" if passed else "error ❌")

if __name__ == '__main__':
    api_test()