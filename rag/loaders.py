"""Lectura de documentos en distintos formatos como texto plano."""

import re
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
    header = None
    rows = []  # (page, cells) of the whole document: additive rows may come after their base
    for number, page in enumerate(reader.pages, start=1):
        layout = (page.extract_text(extraction_mode="layout") or "").strip()
        if not layout:
            text = _image_page_to_text(page)
            if text:
                pages.append(PageText(text=text, page=number))
            continue

        # ponytail: table = columns split by 2+ spaces in layout mode, one header per document;
        # breaks on empty cells, pdfplumber extract_tables is the upgrade path
        prose = []
        last = None  # (cells, starts) of the header/row right above, for wrapped cells
        for line in layout.splitlines():
            spans = [(m.start(), m.group()) for m in re.finditer(r"\S+(?: \S+)*", line)]
            cells = [text for _, text in spans]
            if not cells:
                last = None
            elif last and len(cells) < len(last[0]):
                # wrapped cell: each piece belongs to the column that starts closest to it
                target, starts = last
                for start, text in spans:
                    column = min(range(len(starts)), key=lambda i: abs(starts[i] - start))
                    target[column] += " " + text
            elif header is None and len(cells) >= 3 and not any(c.isdigit() for c in line):
                header = cells
                last = (header, [start for start, _ in spans])
            elif header and len(cells) >= len(header) - 1:
                rows.append((number, cells))
                last = (cells, [start for start, _ in spans])
            else:
                prose.append(" ".join(line.split()))
                last = None
        if prose:
            pages.append(PageText(text="\n".join(prose), page=number))

    # «+N» rows noted "Se suma al supuesto base" (A-07, H-11, H-12) are also written into their
    # base cells: "por fallecimiento (>200 km)" applies to every "Fallecimiento de …" row.
    # ponytail: only rows with that note; B-05/B-06/C-16 «+N» stay alone
    additive = {}
    for _, cells in rows:
        if cells[-1] == "Se suma al supuesto base" and " por " in cells[1]:
            topic = cells[1].split(" por ", 1)[1].split()[0].capitalize() + " de "
            additive.setdefault(topic, []).append(cells)

    for number, cells in rows:
        # one short text per cell: whole rows look alike to the embedding model
        label = f"{cells[0]} {cells[1]}"
        extras = [add for topic, adds in additive.items() if cells[1].startswith(topic) for add in adds]
        for i, (column, value) in enumerate(zip(header[2:], cells[2:]), start=2):
            text = f"{label} · {column}: {value}"
            for add in extras:
                plus = add[i].lstrip("+")
                if value.isdigit() and int(value) and plus.isdigit() and int(plus):
                    text += f". {add[1]} ({add[0]}): {add[i]} = {int(value) + int(plus)} días"
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
