"""Aggregate scoring: combine dimension results into the TARE headline figures."""
from __future__ import annotations

from typing import Any

from . import dimensions as dim
from .models import ServerToolset
from .tokenizer import Tokenizer, serialize_tool

# SPEC.md provisional weights (Reasoned, configurable).
WEIGHTS = {
    "1_tool_surface": 15,
    "2_schema_footprint": 25,
    "3_progressive_disclosure": 20,
    "4_response_discipline": 20,
    "5_description_quality": 10,
    "6_redundancy": 10,
}


def measure(ts: ServerToolset, tok: Tokenizer) -> dict[str, Any]:
    results = [
        dim.tool_surface(ts),
        dim.schema_footprint(ts, tok),
        dim.progressive_disclosure(ts),
        dim.response_discipline(ts),
        dim.description_quality(ts),
        dim.redundancy(ts),
    ]
    by_dim = {r["dimension"]: r for r in results}
    weighted = sum(by_dim[d]["points"] * w for d, w in WEIGHTS.items())
    design_score = round(weighted / sum(WEIGHTS.values()))

    static_context_cost = sum(
        tok.count(serialize_tool(t.name, t.description, t.input_schema)) for t in ts.tools
    )

    return {
        "server": ts.server,
        "source_kind": ts.source_kind,
        "captured_at": ts.captured_at.isoformat(),
        "provenance": ts.provenance,
        "tokenizer": tok.label,
        "tokenizer_is_reference": tok.is_reference,
        "design_score": design_score,
        "static_context_cost": static_context_cost,
        "tool_count": len(ts.tools),
        "dimensions": by_dim,
    }
