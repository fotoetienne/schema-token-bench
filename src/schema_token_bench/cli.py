"""Generate every fixture in every format, count tokens, and write results."""

import argparse
import json
import re
from pathlib import Path

from .count import ClaudeCounter, Counter, TiktokenCounter
from .emitters import BASELINE, FORMATS
from .fixtures import ALL
from .model import Schema

VARIANTS = {
    "documented": lambda s: s,
    "bare": Schema.without_docs,
}
README_START = "<!-- results:start -->"
README_END = "<!-- results:end -->"


def render(schema: Schema, variant: str) -> dict[str, str]:
    s = VARIANTS[variant](schema)
    return {fmt.key: fmt.emit(s) for fmt in FORMATS}


def generate(out: Path) -> list[dict]:
    rows = []
    for schema in ALL:
        for variant in VARIANTS:
            for fmt, text in zip(FORMATS, render(schema, variant).values(), strict=True):
                path = out / schema.name / variant / f"{schema.name}.{fmt.extension}"
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_text(text)
                rows.append(
                    {
                        "fixture": schema.name,
                        "variant": variant,
                        "format": fmt.key,
                        "path": str(path),
                        "bytes": len(text.encode()),
                        "text": text,
                    }
                )
    return rows


def ratio(n: int, base: int) -> str:
    return f"{n / base:.2f}×"


def table(rows: list[dict], metric: str, label: str) -> str:
    """One row per format, one column per fixture/variant, with totals."""
    labels = {f.key: f.label for f in FORMATS}
    kinds = {f.key: f.kind for f in FORMATS}
    cols = [(s.name, v) for v in VARIANTS for s in ALL]
    value = {(r["format"], r["fixture"], r["variant"]): r[metric] for r in rows}

    def total(fmt: str, variant: str) -> int:
        return sum(value[fmt, s.name, variant] for s in ALL)

    header = ["Format", "Kind"] + [f"{s} ({v})" for s, v in cols]
    header += [f"{v} total" for v in VARIANTS] + [f"{v} vs JSON Schema" for v in VARIANTS]
    lines = [f"### {label}", "", "| " + " | ".join(header) + " |", "|" + "---|" * len(header)]
    for fmt in sorted(labels, key=lambda k: total(k, "documented")):
        cells = [labels[fmt], kinds[fmt]] + [str(value[fmt, s, v]) for s, v in cols]
        cells += [str(total(fmt, v)) for v in VARIANTS]
        cells += [ratio(total(fmt, v), total(BASELINE, v)) for v in VARIANTS]
        lines.append("| " + " | ".join(cells) + " |")
    return "\n".join(lines)


def summary(rows: list[dict], counters: list[Counter]) -> str:
    """Totals across all fixtures, one column per tokenizer and variant."""
    labels = {f.key: f.label for f in FORMATS}
    kinds = {f.key: f.kind for f in FORMATS}
    metrics = [(f"tokens:{c.key}", c.label) for c in counters] + [("bytes", "Bytes")]

    def total(fmt: str, metric: str, variant: str) -> int:
        return sum(r[metric] for r in rows if r["format"] == fmt and r["variant"] == variant)

    header = ["Format", "Kind"] + [f"{label}, {v}" for _, label in metrics for v in VARIANTS]
    lines = ["| " + " | ".join(header) + " |", "|---|---|" + "--:|" * (len(header) - 2)]
    first = metrics[0][0]
    for fmt in sorted(labels, key=lambda k: total(k, first, "documented")):
        cells = [labels[fmt], kinds[fmt]]
        for metric, _ in metrics:
            for v in VARIANTS:
                n = total(fmt, metric, v)
                cells.append(f"{n:,} ({ratio(n, total(BASELINE, metric, v))})")
        lines.append("| " + " | ".join(cells) + " |")
    return "\n".join(lines) + "\n"


def report(rows: list[dict], counters: list[Counter]) -> str:
    parts = [table(rows, f"tokens:{c.key}", f"{c.label} tokens") for c in counters]
    parts.append(table(rows, "bytes", "Bytes (UTF-8)"))
    return "\n\n".join(parts) + "\n"


def update_readme(readme: Path, body: str) -> None:
    text = readme.read_text()
    block = f"{README_START}\n{body}{README_END}"
    pattern = re.compile(re.escape(README_START) + ".*?" + re.escape(README_END), re.DOTALL)
    readme.write_text(pattern.sub(lambda _: block, text))


def main() -> None:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument(
        "--model",
        action="append",
        dest="models",
        help="Claude model to count with (repeatable). Default: claude-opus-5-5",
    )
    p.add_argument("--no-claude", action="store_true", help="Skip the Claude count_tokens API")
    p.add_argument("--no-openai", action="store_true", help="Skip tiktoken counts")
    p.add_argument("--generated", type=Path, default=Path("generated"))
    p.add_argument("--results", type=Path, default=Path("results"))
    args = p.parse_args()

    counters: list[Counter] = []
    if not args.no_claude:
        counters += [ClaudeCounter(m) for m in args.models or ["claude-opus-5-5"]]
    if not args.no_openai:
        counters.append(TiktokenCounter("o200k_base"))

    rows = generate(args.generated)
    for row in rows:
        for c in counters:
            row[f"tokens:{c.key}"] = c.count(row["text"])

    args.results.mkdir(exist_ok=True)
    data = [{k: v for k, v in r.items() if k != "text"} for r in rows]
    (args.results / "results.json").write_text(json.dumps(data, indent=2) + "\n")
    totals = summary(rows, counters)
    details = report(rows, counters)
    (args.results / "results.md").write_text(
        f"# Results\n\n## Totals across all fixtures\n\n{totals}\n## Per fixture\n\n{details}"
    )
    if Path("README.md").exists():
        update_readme(Path("README.md"), totals)
    print(totals)


if __name__ == "__main__":
    main()
