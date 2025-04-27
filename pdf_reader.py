"""
PDF Text Extraction Utility

This script extracts text from a PDF file, removes any URLs from the extracted text,
and provides information about the installed pypdf version.
"""

from pypdf import PdfReader
import pypdf
import re

def remove_urls(text: str) -> str:
    """Remove all URLs from the given text."""
    url_pattern = r'https?://\S+|www\.\S+'
    return re.sub(url_pattern, '', text)

def get_text_from_pdf(filepath: str) -> str:
    """Extract text from a PDF file and remove URLs."""
    reader = PdfReader(filepath)
    full_text = ""

    # Iterate through all pages and extract text
    for x in range(len(reader.pages)):
        page = reader.pages[x]
        text = page.extract_text()
        text_without_url = remove_urls(text)
        full_text += text_without_url

    return full_text

def get_pdf_reader_version() -> str:
    """Return the current version of the pypdf library."""
    return f"pypdf {pypdf.__version__}"
