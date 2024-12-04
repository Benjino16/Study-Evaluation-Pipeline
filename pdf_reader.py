from pypdf import PdfReader
import re

def remove_urls(text):
    url_pattern = r'https?://\S+|www\.\S+'
    return re.sub(url_pattern, '', text)

def get_text_from_pdf(filepath: str) -> str:
    reader = PdfReader(filepath)
    full_text = ""

    for x in range(0, len(reader.pages)):
        page = reader.pages[x]
        text = page.extract_text()
        text_without_url = remove_urls(text)
        full_text += text_without_url

    return full_text