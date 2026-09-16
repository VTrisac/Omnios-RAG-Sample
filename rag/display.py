"""Formateo de resultados de búsqueda en terminal con `rich`."""

import re

from rich.console import Console
from rich.panel import Panel
from rich.text import Text

import config
from rag.retriever import SearchResult

console = Console()


def show_results(query: str, results: list[SearchResult], elapsed: float, show_full: bool) -> None:
    """Imprime la cabecera con la pregunta y un panel por cada resultado."""
    console.print()
    console.print(f"[bold]Pregunta:[/bold] {query}")
    console.print(f"[dim]{len(results)} resultados en {elapsed:.2f}s[/dim]")
    console.print()

    if not results:
        console.print("[yellow]No se encontraron resultados.[/yellow]")
        return

    for rank, result in enumerate(results, start=1):
        chunk = result.chunk
        text = chunk.text if show_full else _truncate(chunk.text, config.TRUNCATE_LENGTH)
        body = _highlight(text, query)

        location = chunk.document
        if chunk.page is not None:
            location += f" · página {chunk.page}"

        title = f"#{rank}  score {result.score:.3f}"
        console.print(
            Panel(body, title=title, subtitle=location, subtitle_align="left", border_style="cyan")
        )


def _truncate(text: str, length: int) -> str:
    if len(text) <= length:
        return text
    return text[:length].rstrip() + "…"


def _highlight(text: str, query: str) -> Text:
    styled = Text(text)
    terms = {term for term in re.findall(r"\w+", query.lower()) if len(term) > 2}
    lower_text = text.lower()
    for term in terms:
        start = 0
        while True:
            idx = lower_text.find(term, start)
            if idx == -1:
                break
            styled.stylize("bold yellow", idx, idx + len(term))
            start = idx + len(term)
    return styled
