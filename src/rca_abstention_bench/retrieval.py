"""Keyword search (BM25) over the runbook lines in data/kb/."""

import re
from pathlib import Path

from rank_bm25 import BM25Okapi

from rca_abstention_bench.pilot_data import PROJECT_ROOT

KB_DIR = PROJECT_ROOT / "data" / "kb"


def tokenize(text: str) -> list[str]:
    return re.findall(r"\w+", text.lower())


class RunbookIndex:
    """Each non-empty runbook line is one searchable chunk."""

    def __init__(self, kb_dir: Path = KB_DIR):
        self.chunks: list[tuple[str, str]] = []  # (runbook id, line text)
        for path in sorted(kb_dir.glob("rb-*.md")):
            for line in path.read_text(encoding="utf-8").splitlines():
                if line.strip():
                    self.chunks.append((path.stem, line.strip()))
        self._bm25 = BM25Okapi([tokenize(f"{rb} {text}") for rb, text in self.chunks])

    def search(self, query: str, k: int = 4) -> list[str]:
        scores = self._bm25.get_scores(tokenize(query))
        best = sorted(range(len(self.chunks)), key=lambda i: scores[i], reverse=True)[:k]
        return [f"[{self.chunks[i][0]}] {self.chunks[i][1]}" for i in best]
