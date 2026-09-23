"""Lectura de documentos en distintos formatos como texto plano."""

import base64
import io
import os
from dataclasses import dataclass
from pathlib import Path
from typing import Optional

import anthropic
import pytesseract
from docx import Document as DocxDocument
from PIL import Image
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
    """Página sin capa de texto (escaneo, diagrama): visión con Claude si hay API key; si no, OCR."""
    images = [img.image for img in page.images]
    if not images:
        return ""
    if os.environ.get("ANTHROPIC_API_KEY"):
        try:
            text = _describe_with_claude(images)
        except anthropic.APIError:
            text = ""  # ponytail: degrade to OCR instead of losing the page
        if text:
            return text
    return "\n".join(
        pytesseract.image_to_string(image, lang=config.OCR_LANG) for image in images
    ).strip()


def _describe_with_claude(images: list[Image.Image]) -> str:
    content = []
    for image in images:
        buffer = io.BytesIO()
        image.convert("RGB").save(buffer, format="JPEG", quality=90)
        content.append(
            {
                "type": "image",
                "source": {
                    "type": "base64",
                    "media_type": "image/jpeg",
                    "data": base64.standard_b64encode(buffer.getvalue()).decode(),
                },
            }
        )
    content.append({"type": "text", "text": config.VISION_PROMPT})
    response = anthropic.Anthropic().messages.create(
        model=config.VISION_MODEL,
        max_tokens=16000,
        messages=[{"role": "user", "content": content}],
    )
    if response.stop_reason == "refusal":
        return ""
    return "\n".join(b.text for b in response.content if b.type == "text").strip()


def _load_docx(path: Path) -> list[PageText]:
    document = DocxDocument(str(path))
    text = "\n".join(p.text for p in document.paragraphs if p.text.strip())
    return [PageText(text=text, page=None)] if text.strip() else []


def _load_text(path: Path) -> list[PageText]:
    text = path.read_text(encoding="utf-8", errors="ignore")
    return [PageText(text=text, page=None)] if text.strip() else []
