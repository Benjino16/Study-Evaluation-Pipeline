from datetime import datetime

def process_test_pipeline(prompt: str, filename: str, model: str, temperature: float) -> str:
    """
    Returns a standart text, to test the pipeline without using the APIs.

    Returns:
        str: The result text.

    Raises:
        Exception: The model test-exception will throw exceptions, to test exceptions handling.
    """

    if model == "test-exception":
        raise Exception(f"Run failed with \n status: Test Exception thrown")

    timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
    res_txt = (
        "This is an standart text to test the pipeline.\n"
        f"Model: {model}\n"
        f"Temp: {temperature}\n"
        f"Date: {timestamp}\n"
    )
            
    return res_txt