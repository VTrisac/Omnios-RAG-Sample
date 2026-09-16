import pytest

from rag.chunking import chunk_text


def test_chunk_text_empty():
    assert chunk_text("", chunk_size=800, overlap=100) == []


def test_chunk_text_short_text_single_chunk():
    text = "hola mundo"
    assert chunk_text(text, chunk_size=800, overlap=100) == ["hola mundo"]


def test_chunk_text_splits_with_overlap():
    text = "a" * 1000
    chunks = chunk_text(text, chunk_size=800, overlap=100)
    assert len(chunks) == 2
    assert chunks[0] == "a" * 800
    assert len(chunks[1]) == 300


def test_chunk_text_invalid_overlap():
    with pytest.raises(ValueError):
        chunk_text("texto", chunk_size=100, overlap=100)
