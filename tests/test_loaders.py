import shutil
from pathlib import Path

import pytest

import config
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


@pytest.mark.skipif(not shutil.which("tesseract"), reason="requiere el binario tesseract")
def test_scanned_pdf_falls_back_to_ocr():
    pages = load_document(config.DATA_DIR / "PRO-OPS-007_escalado_incidencias_rev3.pdf")

    assert len(pages) == 1
    assert "Escalado de incidencias" in pages[0].text


def test_pdf_table_rows_carry_column_names():
    pages = load_document(config.DATA_DIR / "politica_permisos_retribuidos_grupo_norvent_2024.pdf")

    assert any(p.text == "H-11 Desplazamiento adicional por fallecimiento (>200 km) · España: +2" for p in pages)
    assert any(p.text == "A-01 Matrimonio del empleado/a · España: 15" for p in pages)


def test_pdf_additive_rows_are_added_to_their_base_case():
    pages = load_document(config.DATA_DIR / "politica_permisos_retribuidos_grupo_norvent_2024.pdf")

    assert any(
        p.text.startswith("H-05 Fallecimiento de abuelo/a · Chile: 1. ")
        and "(H-11): +2 = 3 días" in p.text
        for p in pages
    )


def test_pdf_wrapped_cells_are_joined():
    iberflex = load_document(config.DATA_DIR / "auditoria_proveedor_iberflex_2024.pdf")
    report = load_document(config.DATA_DIR / "IT-2024-041_informe_tecnico.pdf")

    assert any(
        p.text.startswith("NC-PRV-2024-021 Mayor · Descripción: Uso de compuesto")
        and p.text.endswith("sin notificación a Norvent")
        for p in iberflex
    )
    assert any(
        p.text.endswith("Riesgo estimado: Fallo prematuro de rodamiento en 800-2.000 h") for p in report
    )
