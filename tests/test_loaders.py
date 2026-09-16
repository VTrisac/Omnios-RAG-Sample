from pathlib import Path

import pytest

from rag.loaders import DocumentLoadError, load_document


def test_load_text_file(tmp_path: Path):
    file_path = tmp_path / "doc.txt"
    file_path.write_text("Contenido de prueba", encoding="utf-8")

    pages = load_document(file_path)

    assert len(pages) == 1
    assert pages[0].text == "Contenido de prueba"
    assert pages[0].page is None


def test_load_markdown_file(tmp_path: Path):
    file_path = tmp_path / "doc.md"
    file_path.write_text("# Título\n\nTexto de ejemplo", encoding="utf-8")

    pages = load_document(file_path)

    assert "Título" in pages[0].text


def test_load_empty_text_file_returns_no_pages(tmp_path: Path):
    file_path = tmp_path / "empty.txt"
    file_path.write_text("   ", encoding="utf-8")

    assert load_document(file_path) == []


def test_load_unsupported_format_raises(tmp_path: Path):
    file_path = tmp_path / "doc.csv"
    file_path.write_text("a,b,c", encoding="utf-8")

    with pytest.raises(DocumentLoadError):
        load_document(file_path)
