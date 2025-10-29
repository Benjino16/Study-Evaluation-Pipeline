import os
from sep.env_manager import PDF_FOLDER

def _get_schemas() -> list[str]:
    """
    Get all schema folder names inside the PDF folder.
    Example: ['main', 'validation']
    """
    if not os.path.exists(PDF_FOLDER):
        raise FileNotFoundError(f"PDF folder not found: {PDF_FOLDER}")

    return [
        name
        for name in os.listdir(PDF_FOLDER)
        if os.path.isdir(os.path.join(PDF_FOLDER, name))
    ]


def get_path_from_id(file_id: int) -> str:
    """
    Return the full path to a paper by its ID.
    Searches all schema folders and returns the first match.

    Args:
        file_id (int): Paper ID, e.g. 5 or 319.

    Returns:
        str: Path to the PDF file.
    """
    filename = f"{file_id:04d}.pdf"

    for schema in _get_schemas():
        path = os.path.join(PDF_FOLDER, schema, filename)
        if os.path.exists(path):
            return path

    raise FileNotFoundError(f"No paper found with ID {file_id} in any schema.")


def get_id_from_path(path: str) -> int:
    """
    Get the numeric ID from a PDF file path.

    Args:
        path (str): Full or relative path to a PDF file.

    Returns:
        int: Numeric paper ID (e.g. 5 for '0005.pdf').
    """
    filename = os.path.basename(path)
    file_id_str, ext = os.path.splitext(filename)

    if ext.lower() != ".pdf":
        raise ValueError(f"Invalid file extension: {ext}. Expected '.pdf'.")

    if not file_id_str.isdigit():
        raise ValueError(f"Invalid file name: {filename}. Expected like '0005.pdf'.")

    return int(file_id_str)


def get_papers_from_schema(schema: str) -> list[str]:
    """
    List all PDF file paths inside a schema folder.

    Args:
        schema (str): Name of the schema folder.

    Returns:
        list[str]: List of PDF file paths.
    """
    schemas = _get_schemas()
    if schema not in schemas:
        raise ValueError(f"Schema '{schema}' not found. Available: {schemas}")

    folder = os.path.join(PDF_FOLDER, schema)

    papers = [
        os.path.join(folder, f)
        for f in os.listdir(folder)
        if f.lower().endswith(".pdf")
    ]
    return sorted(papers)