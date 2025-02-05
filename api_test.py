from gemini_pipeline import test_gemini_pipeline
from gpt_pipeline import test_gpt_pipeline
from ollama_pipeline import test_ollama_pipeline


def api_test():

    print("---- API Test ----")

    print("testing gpt api...")
    gpt_pipeline = test_gpt_pipeline()
    print("passed ✅" if gpt_pipeline else "error")

    print("testing gemini api...")
    gemini_pipeline = test_gemini_pipeline() 
    print("passed ✅" if gemini_pipeline else "error")

    print("testing ollama api...")
    ollama_pipeline = test_ollama_pipeline() 
    print("passed ✅" if ollama_pipeline else "error")
    
    return {
        "gpt": gpt_pipeline,
        "gemini": gemini_pipeline,
        "ollama": ollama_pipeline,
        "local": False
    }



if __name__ == '__main__':
    api_test()
