"""Tokenization for TARE.

The reference encoding is o200k_base (declared in SPEC.md). Token counts are
tokenizer-dependent, so every result records which tokenizer produced it.

An 'approx' mode (rough char-based estimate) exists ONLY for offline smoke tests
and CI where the o200k_base vocab cannot be downloaded. Approx output is clearly
labelled and must never be published as a real measurement.
"""
from __future__ import annotations

import json
from typing import Any

REFERENCE_ENCODING = "o200k_base"


class Tokenizer:
    def __init__(self, mode: str = REFERENCE_ENCODING):
        self.mode = mode
        self._enc = None
        if mode == REFERENCE_ENCODING:
            import tiktoken  # imported lazily so approx mode needs no network

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
