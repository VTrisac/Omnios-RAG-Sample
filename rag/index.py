"""Construcción, guardado, carga y detección de cambios del índice."""

import json
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Optional

import numpy as np
from rich.console import Console
from rich.progress import track

import config
from rag.chunking import chunk_text
from rag.embeddings import encode
from rag.loaders import DocumentLoadError, load_document

console = Console()


@dataclass
class Chunk:
    """Un fragmento indexado con su procedencia."""

    id: str
    document: str
    page: Optional[int]
    position: int
    text: str


def _iter_data_files() -> list[Path]:
    if not config.DATA_DIR.exists():
        return []
    return sorted(
        p
        for p in config.DATA_DIR.rglob("*")
        if p.is_file() and p.suffix.lower() in config.SUPPORTED_EXTENSIONS
    )


def _compute_signature(files: list[Path]) -> dict[str, list]:
    signature = {}
    for file_path in files:
        stat = file_path.stat()
        key = str(file_path.relative_to(config.DATA_DIR))
        signature[key] = [stat.st_size, int(stat.st_mtime)]
    return signature


def needs_reindex() -> bool:
    """Indica si el índice no existe o si los documentos de `data/` han cambiado."""
    if not config.INDEX_METADATA_PATH.exists() or not config.INDEX_EMBEDDINGS_PATH.exists():
        return True
    try:
        saved = json.loads(config.INDEX_METADATA_PATH.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        return True
    return saved.get("signature") != _compute_signature(_iter_data_files())


def build_index() -> None:
    """Reconstruye el índice completo a partir de los documentos en `data/`."""
    files = _iter_data_files()
    if not files:
        raise FileNotFoundError(
            f"No se encontraron documentos soportados en '{config.DATA_DIR}'. "
            f"Añade archivos {', '.join(sorted(config.SUPPORTED_EXTENSIONS))} para indexar."
        )

    chunks: list[Chunk] = []
    for file_path in track(files, description="Leyendo documentos...", console=console):
        try:
            pages = load_document(file_path)
        except DocumentLoadError as exc:
            console.print(f"[yellow]Aviso:[/yellow] {exc}")
            continue

        rel_name = str(file_path.relative_to(config.DATA_DIR))
        position = 0
        for page in pages:
            for fragment in chunk_text(page.text, config.CHUNK_SIZE, config.CHUNK_OVERLAP):
                chunks.append(
                    Chunk(
                        id=f"{rel_name}#{position}",
                        document=rel_name,
                        page=page.page,
                        position=position,
                        text=fragment,
                    )
                )
                position += 1
        if position == 0:
            console.print(f"[yellow]Aviso:[/yellow] '{rel_name}' no tiene texto extraíble; no se indexa.")

    if not chunks:
        raise ValueError("Los documentos de 'data/' no contienen texto extraíble.")

    console.print(f"Generando embeddings para {len(chunks)} fragmentos...")
    embeddings = encode([c.text for c in chunks], show_progress=True)

    config.INDEX_DIR.mkdir(parents=True, exist_ok=True)
    np.save(config.INDEX_EMBEDDINGS_PATH, embeddings)
    metadata = {
        "signature": _compute_signature(files),
        "model": config.EMBEDDING_MODEL_NAME,
        "chunks": [asdict(c) for c in chunks],
    }
    config.INDEX_METADATA_PATH.write_text(
        json.dumps(metadata, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    console.print(f"[green]Índice construido con {len(chunks)} fragmentos.[/green]")


def load_index() -> tuple[np.ndarray, list[Chunk]]:
    """Carga los embeddings y metadatos del índice guardado en disco."""
    if not config.INDEX_EMBEDDINGS_PATH.exists() or not config.INDEX_METADATA_PATH.exists():
        raise FileNotFoundError("El índice no existe todavía. Ejecuta 'python run.py --reindex'.")
    embeddings = np.load(config.INDEX_EMBEDDINGS_PATH)
    metadata = json.loads(config.INDEX_METADATA_PATH.read_text(encoding="utf-8"))
    chunks = [Chunk(**c) for c in metadata["chunks"]]
    return embeddings, chunks
