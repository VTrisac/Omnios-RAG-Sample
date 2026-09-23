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

# Páginas sin capa de texto (PDF escaneado): visión con Claude si hay ANTHROPIC_API_KEY, si no OCR
OCR_LANG = "spa"
VISION_MODEL = "claude-opus-5"
VISION_PROMPT = (
    "Transcribe esta página para un índice de búsqueda. Copia todo el texto visible. "
    "Si contiene un diagrama de flujo, descríbelo completo en frases explícitas: cada carril/rol, "
    "cada paso, cada decisión con sus ramas (\"Si X, entonces Y\"), a quién se escala, plazos y "
    "significado de colores, bordes y tipos de línea según la leyenda. Responde en el idioma del "
    "documento, solo texto plano."
)

# Formatos de documento soportados
SUPPORTED_EXTENSIONS = {".pdf", ".docx", ".txt", ".md"}
