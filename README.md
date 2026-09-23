# Omnios RAG Sample

Recuperación semántica sobre los documentos de `data/` (`.pdf`, `.docx`, `.txt`, `.md`). Recibe una pregunta por CLI y devuelve los fragmentos más relevantes. Sin generación con LLM.

## Instalación

Requiere Python 3.10+.

```bash
python -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r requirements.txt
brew install tesseract tesseract-lang   # Debian/Ubuntu: apt install tesseract-ocr tesseract-ocr-spa
```

Las páginas de PDF sin capa de texto (escaneos, diagramas) se transcriben con visión de Claude si
`ANTHROPIC_API_KEY` está definida; si no, con OCR (Tesseract). Tras cambiar de modo, `--reindex`.

## Uso

```bash
python run.py "¿pregunta?"
```

El índice se construye automáticamente la primera vez y se reconstruye si `data/` cambia.

| Opción | Descripción |
|---|---|
| `--reindex` | Fuerza la reconstrucción del índice |
| `--top-k N` | Número de fragmentos a devolver |
| `--show-full` | Muestra el fragmento completo sin truncar |

Configuración (modelo, chunk size, top-k, rutas) en `config.py`. Tests: `pytest`.
