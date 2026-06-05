"""Tokenization for TARE.

The reference encoding is o200k_base (declared in SPEC.md). Token counts are
tokenizer-dependent, so every result records which tokenizer produced it.

An 'approx' mode (rough char-based estimate) exists ONLY for offline smoke tests
and CI where the o200k_base vocab cannot be downloaded. Approx output is clearly
labelled and must never be published as a real measurement.
"""
from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Any

REFERENCE_ENCODING = "o200k_base"

# Vendored o200k_base vocab so the reference tokenizer works fully offline (CI,
# sandboxed environments). The file is named by tiktoken's cache key, which is
# sha1("https://openaipublic.blob.core.windows.net/encodings/o200k_base.tiktoken").
# SHA256 of the vocab is 446a9538cb6c348e3516120d7c08b09f57c36495e2acfffe59a5bf8b0cfb1a2d
# (matches the official OpenAI file). tiktoken supplies the regex + special tokens.
_VENDORED_CACHE_DIR = Path(__file__).resolve().parent.parent / "vendor" / "tiktoken"


def _ensure_offline_vocab() -> None:
    """Point tiktoken at the vendored vocab when no cache dir is already set."""
    if os.environ.get("TIKTOKEN_CACHE_DIR"):
        return
    if _VENDORED_CACHE_DIR.is_dir():
        os.environ["TIKTOKEN_CACHE_DIR"] = str(_VENDORED_CACHE_DIR)


class Tokenizer:
    def __init__(self, mode: str = REFERENCE_ENCODING):
        self.mode = mode
        self._enc = None
        if mode == REFERENCE_ENCODING:
            import tiktoken  # imported lazily so approx mode needs no network

            _ensure_offline_vocab()
            self._enc = tiktoken.get_encoding(REFERENCE_ENCODING)
        elif mode != "approx":
            raise ValueError(f"unknown tokenizer mode: {mode}")

    @property
    def label(self) -> str:
        return REFERENCE_ENCODING if self._enc is not None else "approx(char/4)"

    @property
    def is_reference(self) -> bool:
        return self._enc is not None

    def count(self, text: str) -> int:
        if self._enc is not None:
            return len(self._enc.encode(text))
        return max(1, round(len(text) / 4))


def serialize_tool(name: str, description: str | None, input_schema: dict[str, Any]) -> str:
    """TARE reference serialization of a tool definition for tokenization.

    Real clients serialize tool definitions differently. This is the declared,
    reproducible reference shape so that footprints are comparable across servers.
    """
    payload = {
        "name": name,
        "description": description or "",
        "inputSchema": input_schema or {},
    }
    return json.dumps(payload, sort_keys=True, separators=(",", ":"), ensure_ascii=False)
