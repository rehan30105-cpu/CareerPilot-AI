"""PDF text extraction and resume metadata parsing.

Provides PDF text extraction with PyMuPDF (fitz) as the primary parser,
with a fallback path for environments where PyMuPDF is not installed.

Usage:
    from app.services.parsing import extract_text_from_pdf
    result = extract_text_from_pdf("resume.pdf")
"""

import logging
from pathlib import Path
from typing import NamedTuple

logger = logging.getLogger(__name__)

try:
    import fitz  # PyMuPDF

    HAS_PYMUPF = True
except ImportError:
    HAS_PYMUPF = False


class PDFResult(NamedTuple):
    """Result of PDF text extraction."""

    text: str
    page_count: int
    has_scanned_content: bool
    empty: bool
    error: str | None = None


def extract_text_from_pdf(file_path: str | Path) -> PDFResult:
    """Extract text from a PDF file.

    Uses PyMuPDF (fitz) for fast, reliable text extraction when available.
    Falls back to a minimal implementation if PyMuPDF is not installed.

    Returns:
        PDFResult with extracted text, page count, and flags.
    """
    path = Path(file_path)
    if not path.exists():
        return PDFResult("", 0, False, True, "File not found")

    # Check file size limit (10 MB)
    max_size = 10 * 1024 * 1024  # 10 MB
    if path.stat().st_size > max_size:
        return PDFResult("", 0, False, True, "File exceeds 10 MB limit")

    if HAS_PYMUPF:
        # PyMuPDF path
        try:
            doc = fitz.open(path)
        except Exception as exc:
            return PDFResult("", 0, False, True, f"Failed to open PDF: {exc}")

        if doc.page_count == 0:
            doc.close()
            return PDFResult("", 0, False, True, "PDF has no pages")

        # Extract text from all pages
        text_parts = []
        for page_num, page in enumerate(doc):
            page_text = page.get_text("text")
            text_parts.append(page_text)

            # Check for images on this page (potential scanned content)
            page_images = page.get_images()
            if page_images:
                pass

        doc.close()

        full_text = "\n".join(text_parts)
        word_count = len(full_text.split())

        # Heuristic: PDFs with mostly images (scanned) either have no text
        # or very few words relative to pages
        has_scanned_content = bool(doc.page_count and word_count < doc.page_count * 5)

        # Empty if no text or only very few words
        empty = word_count < 10

        logger.info(
            "PDF extracted",
            extra={
                "file": path.name,
                "pages": doc.page_count if "doc" in dir() else 0,
                "word_count": word_count,
                "empty": empty,
            },
        )

        return PDFResult(
            text=full_text,
            page_count=doc.page_count if "doc" in dir() else 0,
            has_scanned_content=has_scanned_content,
            empty=empty,
            error=None,
        )
    else:
        # Fallback when PyMuPDF is not installed
        # Simple text extraction not available; return minimal result
        return PDFResult(
            text="",
            page_count=0,
            has_scanned_content=False,
            empty=True,
            error="PyMuPDF not installed. Install PyMuPDF for PDF text extraction.",
        )


class PDFResult(NamedTuple):
    """Result of PDF text extraction."""

    text: str
    page_count: int
    has_scanned_content: bool
    empty: bool
    error: str | None = None


def extract_text_from_pdf(file_path: str | Path) -> PDFResult:
    """Extract text from a PDF file.

    Uses PyMuPDF (fitz) for fast, reliable text extraction.

    Returns:
        PDFResult with extracted text, page count, and flags.
    """
    path = Path(file_path)
    if not path.exists():
        return PDFResult("", 0, False, True, "File not found")

    # Check file size limit (10 MB)
    max_size = 10 * 1024 * 1024  # 10 MB
    if path.stat().st_size > max_size:
        return PDFResult("", 0, False, True, "File exceeds 10 MB limit")

    try:
        doc = fitz.open(path)
    except Exception as exc:
        return PDFResult("", 0, False, True, f"Failed to open PDF: {exc}")

    if doc.page_count == 0:
        doc.close()
        return PDFResult("", 0, False, True, "PDF has no pages")

    # Extract text from all pages
    text_parts = []
    for page_num, page in enumerate(doc):
        page_text = page.get_text("text")
        text_parts.append(page_text)

        # Check for images on this page (potential scanned content)
        page_images = page.get_images()
        if page_images:
            # Get text as well - images with text would still have text
            pass

    doc.close()

    full_text = "\n".join(text_parts)
    word_count = len(full_text.split())

    # Heuristic: PDFs with mostly images (scanned) either have no text
    # or very few words relative to pages
    has_scanned_content = bool(doc.page_count and word_count < doc.page_count * 5)

    # Empty if no text or only very few words
    empty = word_count < 10

    logger.info(
        "PDF extracted",
        extra={
            "file": path.name,
            "pages": doc.page_count if "doc" in dir() else 0,
            "word_count": word_count,
            "empty": empty,
        },
    )

    return PDFResult(
        text=full_text,
        page_count=doc.page_count if "doc" in dir() else 0,
        has_scanned_content=has_scanned_content,
        empty=empty,
        error=None,
    )


def extract_text_with_fallback(file_path: str | Path) -> PDFResult:
    """Attempt PyMuPDF extraction, falling back to pypdf if needed.

    This provides compatibility if PyMuPDF is not installed.
    """
    result = extract_text_from_pdf(file_path)

    if result.empty and result.error:
        # PyMuPDF failed, try pypdf as fallback
        try:
            from pypdf import PdfReader

            reader = PdfReader(str(file_path))
            text_parts = []
            for page in reader.pages:
                text = page.extract_text()
                if text:
                    text_parts.append(text)

            full_text = "\n".join(text_parts)
            word_count = len(full_text.split())

            return PDFResult(
                text=full_text,
                page_count=len(reader.pages),
                has_scanned_content=False,
                empty=word_count < 10,
                error=None,
            )
        except ImportError:
            # pypdf not installed, return PyMuPDF error
            return result
        except Exception as exc:
            return PDFResult(
                "",
                0,
                False,
                True,
                f"pypdf fallback also failed: {exc}",
            )

    return result
