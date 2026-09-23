"""Parámetros de configuración del sistema de recuperación."""

from pathlib import Path

# Rutas
BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "data"
INDEX_DIR = BASE_DIR / ".index"
INDEX_EMBEDDINGS_PATH = INDEX_DIR / "embeddings.npy"
INDEX_METADATA_PATH = INDEX_DIR / "metadata.json"

# Modelo de embeddings (multilingüe, ligero, apto para CPU)
EMBEDDING_MODEL_NAME = "paraphrase-multilingual-MiniLM-L12-v2"

# Chunking
CHUNK_SIZE = 800
CHUNK_OVERLAP = 100

# Recuperación
TOP_K = 5
TRUNCATE_LENGTH = 400

# OCR para páginas de PDF sin capa de texto (escaneos)
OCR_LANG = "spa"

# Formatos de documento soportados
SUPPORTED_EXTENSIONS = {".pdf", ".docx", ".txt", ".md"}
