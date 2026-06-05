"""Build the TARE-Bench leaderboard from per-server result files."""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any


def load_results(results_dir: str) -> list[dict[str, Any]]:
    out = []
    for p in sorted(Path(results_dir).glob("*.json")):
        out.append(json.loads(p.read_text(encoding="utf-8")))
    return out


def leaderboard_markdown(results: list[dict[str, Any]]) -> str:
    rows = sorted(results, key=lambda r: r["design_score"], reverse=True)
    tokenizers = {r["tokenizer"] for r in rows}
    approx = any(not r.get("tokenizer_is_reference", True) for r in rows)

    lines = ["# TARE-Bench v0 Leaderboard", ""]
    lines.append(f"Tokenizer: {', '.join(sorted(tokenizers))}")
    if approx:
        lines.append("")
        lines.append("> WARNING: at least one row used the approx tokenizer. "
                     "These are smoke-test numbers, not publishable measurements.")
    lines += ["", "| Server | Design Score | Static Context Cost (tokens) | Tools | "
              "Surface | Schema | Prog. Disclosure | Response | Descriptions | Redundancy | Source |",
              "|---|---|---|---|---|---|---|---|---|---|---|"]
    for r in rows:
        d = r["dimensions"]
        lines.append(
            f"| {r['server']} | {r['design_score']} | {r['static_context_cost']:,} | "
            f"{r['tool_count']} | {d['1_tool_surface']['band']} | "
            f"{d['2_schema_footprint']['band']} | {d['3_progressive_disclosure']['band']} | "
            f"{d['4_response_discipline']['band']} | {d['5_description_quality']['band']} | "
            f"{d['6_redundancy']['band']} | {r['source_kind']} |"
        )
    lines.append("")
    lines.append("Bands: green / yellow / red (full / partial / none for progressive disclosure). "
                 "Design Score is a 0-100 composite; Static Context Cost is the ground-truth token "
                 "footprint at default load. See docs/SPEC.md.")
    return "\n".join(lines)
