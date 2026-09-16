#!/usr/bin/env python
"""CLI del sistema de recuperación semántica."""

import argparse
import sys

import config
from rag import display
from rag.index import build_index, needs_reindex
from rag.retriever import search


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Recupera los fragmentos más relevantes de los documentos en 'data/'."
    )
    parser.add_argument("pregunta", nargs="?", help="Pregunta en lenguaje natural")
    parser.add_argument("--reindex", action="store_true", help="Fuerza la reconstrucción del índice")
    parser.add_argument("--top-k", type=int, default=config.TOP_K, help="Número de resultados a mostrar")
    parser.add_argument(
        "--show-full", action="store_true", help="Muestra el fragmento completo sin truncar"
    )
    args = parser.parse_args()

    if not args.pregunta and not args.reindex:
        parser.error('Debes indicar una pregunta, por ejemplo: python run.py "¿qué es X?"')

    try:
        if args.reindex or needs_reindex():
            build_index()
    except (FileNotFoundError, ValueError) as exc:
        print(f"Error: {exc}", file=sys.stderr)
        sys.exit(1)

    if not args.pregunta:
        return

    try:
        results, elapsed = search(args.pregunta, top_k=args.top_k)
    except FileNotFoundError as exc:
        print(f"Error: {exc}", file=sys.stderr)
        sys.exit(1)

    display.show_results(args.pregunta, results, elapsed, args.show_full)


if __name__ == "__main__":
    main()
