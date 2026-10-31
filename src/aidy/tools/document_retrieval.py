"""Uploaded document retrieval tool for processing local academic PDFs, DOCX, and text files."""

import os
from typing import Optional
from aidy.core.exceptions import WebRetrievalError
from aidy.core.security import sanitize_untrusted_content
from aidy.core.logging import logger


def read_uploaded_file(file_path: str, max_chars: int = 20000) -> str:
    """Extracts text from local text, markdown, docx, or PDF files safely."""
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"File not found at {file_path}")

    ext = os.path.splitext(file_path)[1].lower()
    logger.info(f"Extracting document text from {file_path} (format: {ext})")

    extracted_text = ""
    try:
        if ext in (".txt", ".md", ".csv", ".json"):
            with open(file_path, "r", encoding="utf-8", errors="replace") as f:
                extracted_text = f.read()

        elif ext == ".docx":
            import docx
            doc = docx.Document(file_path)
            extracted_text = "\n".join([p.text for p in doc.paragraphs if p.text.strip()])

        elif ext == ".pdf":
            try:
                import fitz  # PyMuPDF
                doc = fitz.open(file_path)
                pages = [page.get_text() for page in doc]
                extracted_text = "\n\n".join(pages)
                doc.close()
            except ImportError:
                from pypdf import PdfReader
                reader = PdfReader(file_path)
                extracted_text = "\n\n".join([page.extract_text() or "" for page in reader.pages])

        else:
            raise ValueError(f"Unsupported document format: {ext}")

        sanitized, flagged = sanitize_untrusted_content(extracted_text, max_chars=max_chars)
        return sanitized

    except Exception as e:
        logger.error(f"Error reading document {file_path}: {e}")
        raise WebRetrievalError(f"Failed to extract document contents: {e}") from e
