from sep.api_request.gemini_pipeline import get_gemini_model_name
from sep.api_request.gpt_pipeline import get_gpt_model_name

def get_full_model_name(name: str) -> str:
    """This function receives the name of an AI model as a string and checks the current full name of this model."""
    if name.lower().startswith('gemini'):
        return get_gemini_model_name(name)
    
    elif name.lower().startswith('gpt') or name.lower().startswith('deepseek-chat'):
        return get_gpt_model_name(name)
    
    elif name.lower().startswith('o1'):
        return get_gpt_model_name(name)
    
    elif name.lower().startswith('deepseek'):
        raise("Local model information can not be retrieved.")