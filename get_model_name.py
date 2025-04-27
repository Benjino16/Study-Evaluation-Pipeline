from gemini_pipeline import get_gemini_model_name
from gpt_pipeline import get_gpt_model_name

def get_full_model_name(name: str) -> str:
    if name.lower().startswith('gemini'):
        return get_gemini_model_name(name)
    
    elif name.lower().startswith('gpt') or name.lower().startswith('deepseek-chat'):
        return get_gpt_model_name(name)
    
    elif name.lower().startswith('o1'):
        return get_gpt_model_name(name)
    
    elif name.lower().startswith('deepseek'):
        raise("Local model information can not be retrieved.")