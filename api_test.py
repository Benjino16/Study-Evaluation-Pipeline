from gemini_pipeline import test_gemini_pipeline
from gpt_pipeline import test_gpt_pipeline
from gpt_text_pipeline import test_deepseek_pipeline


def api_test():

    print("---- API Test ----")

    print("testing gpt api...")
    gpt_pipeline = test_gpt_pipeline()
    print("passed ✅" if gpt_pipeline else "error")

    print("testing gemini api...")
    gemini_pipeline = test_gemini_pipeline() 
    print("passed ✅" if gemini_pipeline else "error")

    print("testing deepseek api...")
    deepseek_pipeline = test_deepseek_pipeline() 
    print("passed ✅" if deepseek_pipeline else "error")

    return {
        "gpt": gpt_pipeline,
        "gemini": gemini_pipeline,
        "deepseek": deepseek_pipeline,
        "local": False
    }



if __name__ == '__main__':
    api_test()
