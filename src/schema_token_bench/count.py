"""Token counters. Claude counts come from the count_tokens API and are cached
on disk; OpenAI counts come from tiktoken locally."""

import hashlib
import json
from pathlib import Path
from typing import Protocol

CACHE = Path(".cache/counts.json")


class Counter(Protocol):
    key: str
    label: str

    def count(self, text: str) -> int: ...


class ClaudeCounter:
    """`count_tokens` wraps the text in a user message, which adds a fixed
    overhead. We measure it once with a one-token message and subtract it."""

    def __init__(self, model: str):
        from anthropic import Anthropic

        self.key = model
        self.label = f"Claude ({model})"
        self.client = Anthropic()
        self.cache: dict[str, int] = json.loads(CACHE.read_text()) if CACHE.exists() else {}
        self.overhead = self._raw("x") - 1

    def _raw(self, text: str) -> int:
        digest = hashlib.sha256(text.encode()).hexdigest()
        cache_key = f"{self.key}:{digest}"
        if cache_key not in self.cache:
            resp = self.client.messages.count_tokens(
                model=self.key, messages=[{"role": "user", "content": text}]
            )
            self.cache[cache_key] = resp.input_tokens
            CACHE.parent.mkdir(exist_ok=True)
            CACHE.write_text(json.dumps(self.cache, indent=1, sort_keys=True))
        return self.cache[cache_key]

    def count(self, text: str) -> int:
        return self._raw(text) - self.overhead


class TiktokenCounter:
    def __init__(self, encoding: str = "o200k_base"):
        import tiktoken

        self.key = encoding
        self.label = f"OpenAI ({encoding})"
        self.enc = tiktoken.get_encoding(encoding)

    def count(self, text: str) -> int:
        return len(self.enc.encode(text))
