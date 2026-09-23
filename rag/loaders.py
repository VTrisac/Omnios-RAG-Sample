"""Lectura de documentos en distintos formatos como texto plano."""

from dataclasses import dataclass
from pathlib import Path
from typing import Optional

import pytesseract
from docx import Document as DocxDocument
from pypdf import PdfReader

import config


@dataclass
class PageText:
    """Texto extraído de una página (o de un documento sin paginación)."""

    text: str
    page: Optional[int]


class DocumentLoadError(Exception):
    """Error al leer un documento: formato no soportado o archivo corrupto."""


def load_document(path: Path) -> list[PageText]:
    """Carga un documento y devuelve su texto dividido por página cuando aplica."""
    suffix = path.suffix.lower()
    if suffix == ".pdf":
        loader = _load_pdf
    elif suffix == ".docx":
        loader = _load_docx
    elif suffix in (".txt", ".md"):
        loader = _load_text
    else:
        raise DocumentLoadError(f"Formato no soportado: '{path.suffix}' en '{path.name}'")

    try:
        return loader(path)
    except DocumentLoadError:
        raise
    except Exception as exc:
        raise DocumentLoadError(f"No se pudo leer '{path.name}': {exc}") from exc


def _load_pdf(path: Path) -> list[PageText]:
    reader = PdfReader(str(path))
    pages = []
    for number, page in enumerate(reader.pages, start=1):
        text = (page.extract_text() or "").strip() or _image_page_to_text(page)
        if text:
            pages.append(PageText(text=text, page=number))
    return pages


def _image_page_to_text(page) -> str:
    """OCR de las imágenes de una página sin capa de texto (PDF escaneado)."""
    # ponytail: plain OCR loses diagram structure (arrows, lanes); vision LLM is the upgrade path
    return "\n".join(
        pytesseract.image_to_string(img.image, lang=config.OCR_LANG) for img in page.images
    ).strip()


def _load_docx(path: Path) -> list[PageText]:
    document = DocxDocument(str(path))
    text = "\n".join(p.text for p in document.paragraphs if p.text.strip())
    return [PageText(text=text, page=None)] if text.strip() else []


def _load_text(path: Path) -> list[PageText]:
    text = path.read_text(encoding="utf-8", errors="ignore")
    return [PageText(text=text, page=None)] if text.strip() else []
