"""División de texto en fragmentos de tamaño fijo con solapamiento."""


def chunk_text(text: str, chunk_size: int, overlap: int) -> list[str]:
    """Divide `text` en fragmentos de `chunk_size` caracteres con `overlap` de solapamiento."""
    if overlap >= chunk_size:
        raise ValueError("overlap debe ser menor que chunk_size")

    text = text.strip()
    if not text:
        return []

    chunks = []
    step = chunk_size - overlap
    start = 0
    length = len(text)
    while start < length:
        end = start + chunk_size
        fragment = text[start:end].strip()
        if fragment:
            chunks.append(fragment)
        if end >= length:
            break
        start += step
    return chunks
