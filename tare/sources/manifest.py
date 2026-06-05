"""Manifest source: load a captured tools/list payload from disk.

Fast and partial. Lets a leaderboard ship before every server's auth is sorted.
A manifest is JSON of shape:
    {"captured_at": "...", "provenance": "...", "declares_dynamic_toolsets": false,
     "tools": [ {"name": "...", "description": "...", "inputSchema": {...}}, ... ]}
"""
from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path

from ..models import ServerConfig, ServerToolset, Tool
from .base import ToolSource


def _parse_dt(value) -> datetime:
    if not value:
        return datetime.now(timezone.utc)
    try:
        return datetime.fromisoformat(value)
    except Exception:
        return datetime.now(timezone.utc)


class ManifestSource(ToolSource):
    def fetch(self, config: ServerConfig) -> ServerToolset:
        if not config.manifest_path:
            raise ValueError(f"{config.name}: no manifest_path configured")
        path = Path(config.manifest_path)
        if not path.exists():
            raise FileNotFoundError(
                f"{config.name}: manifest not found at {path}. "
                f"Capture one (see manifests/README.md) or use --source live."
            )
        data = json.loads(path.read_text(encoding="utf-8"))
        if data.get("captured_at") == "UNCAPTURED":
            raise ValueError(
                f"{config.name}: manifest is a stub (captured_at=UNCAPTURED). "
                f"Capture it: {data.get('provenance', 'see manifests/README.md')}"
            )
        tools = [Tool.model_validate(t) for t in data.get("tools", [])]
        return ServerToolset(
            server=config.name,
            source_kind="manifest",
            captured_at=_parse_dt(data.get("captured_at")),
            provenance=data.get("provenance", str(path)),
            declares_dynamic_toolsets=data.get(
                "declares_dynamic_toolsets", config.declares_dynamic_toolsets
            ),
            tools=tools,
        )
