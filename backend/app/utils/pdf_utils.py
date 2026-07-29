import os
from typing import Optional


def extract_text_from_pdf(pdf_path: str) -> Optional[str]:
    """Extracts text from a PDF file using PyPDF2 if available.
    Returns None on failure or if extractor not available.
    """
    try:
        from PyPDF2 import PdfReader
    except Exception:
        return None

    if not os.path.exists(pdf_path):
        return None

    try:
        reader = PdfReader(pdf_path)
        texts = []
        for page in reader.pages:
            try:
                texts.append(page.extract_text() or "")
            except Exception:
                continue
        return "\n\n".join(texts).strip()
    except Exception:
        return None
