"""Shared layout rules. Signatures go on one line when they fit in WIDTH
columns and carry no per-parameter docs, as prettier and black would do."""

WIDTH = 80


def fits(line: str, docs: bool) -> bool:
    return not docs and len(line) <= WIDTH


def blocks(parts: list[str], blank_lines: int = 1) -> str:
    return ("\n" * (blank_lines + 1)).join(p for p in parts if p) + "\n"
