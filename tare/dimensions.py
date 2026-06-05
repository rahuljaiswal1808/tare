"""Static dimension scorers (SPEC.md dimensions 1, 2, 3, 4-static, 5-structural, 6).

Every scorer returns a dict with: dimension, band, points, raw, label.
These are heuristic v0 implementations. Thresholds match SPEC.md and are marked
there with epistemic labels (mostly Reasoned). The runtime half of Dimension 4
and the judged half of Dimension 5 are out of scope for this static harness.
"""
from __future__ import annotations

import json
import statistics
from typing import Any

from .models import ServerToolset
from .tokenizer import Tokenizer, serialize_tool

# Heuristic vocabularies (v0). Documented as heuristics, easy to tune.
_META_TOOL_HINTS = {"search_tools", "list_tools", "find_tools", "list_toolsets",
                    "enable_toolset", "tool_search", "search_for_tools"}
_SHAPING_KEYS = {"limit", "page", "page_size", "pagesize", "cursor", "offset",
                 "fields", "projection", "select", "top", "max_results", "maxresults",
                 "per_page", "perpage", "first", "after"}
_DATA_TOOL_HINTS = ("list", "get", "search", "read", "query", "find", "fetch", "retrieve")
_USAGE_HINTS = ("use this", "use when", "when you", "do not", "don't", "only use",
                "avoid", "prefer", "instead of")

_GREEN, _YELLOW, _RED = "green", "yellow", "red"
_BAND_POINTS = {"green": 100, "yellow": 60, "red": 20,
                "full": 100, "partial": 60, "none": 20}


def band_points(band: str) -> int:
    return _BAND_POINTS[band]


# --- Dimension 1: tool surface economy --------------------------------------
def tool_surface(ts: ServerToolset) -> dict[str, Any]:
    n = len(ts.tools)
    band = _GREEN if n <= 15 else _YELLOW if n <= 30 else _RED
    return {"dimension": "1_tool_surface", "band": band, "points": band_points(band),
            "raw": {"tool_count": n}, "label": "Sourced (10-15 heuristic) / Reasoned"}


# --- Dimension 2: schema footprint ------------------------------------------
def schema_footprint(ts: ServerToolset, tok: Tokenizer) -> dict[str, Any]:
    per_tool = [tok.count(serialize_tool(t.name, t.description, t.input_schema)) for t in ts.tools]
    total = sum(per_tool)
    median = int(statistics.median(per_tool)) if per_tool else 0
    p95 = int(_percentile(per_tool, 95)) if per_tool else 0
    mx = max(per_tool) if per_tool else 0

    pt_band = _GREEN if median <= 400 else _YELLOW if median <= 700 else _RED
    tot_band = _GREEN if total < 6000 else _YELLOW if total <= 15000 else _RED
    points = round((band_points(pt_band) + band_points(tot_band)) / 2)
    worst = min([pt_band, tot_band], key=lambda b: band_points(b))
    return {"dimension": "2_schema_footprint", "band": worst, "points": points,
            "raw": {"total_tokens": total, "median_per_tool": median, "p95_per_tool": p95,
                    "max_per_tool": mx, "tokenizer": tok.label},
            "label": "Reasoned"}


# --- Dimension 3: progressive disclosure ------------------------------------
def progressive_disclosure(ts: ServerToolset) -> dict[str, Any]:
    names = {t.name.lower() for t in ts.tools}
    has_meta = bool(names & _META_TOOL_HINTS) or any("search" in n and "tool" in n for n in names)
    if ts.declares_dynamic_toolsets or has_meta:
        band = "full"
    else:
        band = "none"
    return {"dimension": "3_progressive_disclosure", "band": band, "points": band_points(band),
            "raw": {"declares_dynamic_toolsets": ts.declares_dynamic_toolsets,
                    "meta_tool_detected": has_meta},
            "label": "Reasoned"}


# --- Dimension 4 (static): response discipline ------------------------------
def response_discipline(ts: ServerToolset) -> dict[str, Any]:
    data_tools = [t for t in ts.tools if any(h in t.name.lower() for h in _DATA_TOOL_HINTS)]
    if not data_tools:
        return {"dimension": "4_response_discipline", "band": _GREEN, "points": 100,
                "raw": {"data_tools": 0, "with_shaping": 0}, "label": "Reasoned (no data tools)"}
    with_shaping = 0
    for t in data_tools:
        props = set((t.input_schema or {}).get("properties", {}).keys())
        props_lower = {p.lower() for p in props}
        if props_lower & _SHAPING_KEYS:
            with_shaping += 1
    frac = with_shaping / len(data_tools)
    band = _GREEN if frac >= 0.999 else _YELLOW if frac > 0 else _RED
    return {"dimension": "4_response_discipline", "band": band, "points": band_points(band),
            "raw": {"data_tools": len(data_tools), "with_shaping": with_shaping,
                    "fraction": round(frac, 2)},
            "label": "Reasoned (static capability only)"}


# --- Dimension 5 (structural): description quality --------------------------
def description_quality(ts: ServerToolset) -> dict[str, Any]:
    if not ts.tools:
        return {"dimension": "5_description_quality", "band": _RED, "points": 20,
                "raw": {"tools": 0}, "label": "Reasoned (structural only)"}
    passing = 0
    for t in ts.tools:
        d = (t.description or "").strip()
        has_desc = len(d) > 0
        in_band = 20 <= len(d) <= 1500
        has_usage = any(h in d.lower() for h in _USAGE_HINTS)
        if has_desc and in_band and has_usage:
            passing += 1
    frac = passing / len(ts.tools)
    band = _GREEN if frac >= 0.8 else _YELLOW if frac >= 0.5 else _RED
    return {"dimension": "5_description_quality", "band": band, "points": band_points(band),
            "raw": {"tools": len(ts.tools), "passing": passing, "fraction": round(frac, 2)},
            "label": "Reasoned (structural only)"}


# --- Dimension 6: redundancy and consistency --------------------------------
def redundancy(ts: ServerToolset) -> dict[str, Any]:
    fragments = []
    for t in ts.tools:
        props = (t.input_schema or {}).get("properties", {})
        for _, sub in props.items():
            fragments.append(json.dumps(sub, sort_keys=True, separators=(",", ":")))
    total = len(fragments)
    unique = len(set(fragments))
    ratio = (1 - unique / total) if total else 0.0
    band = _GREEN if ratio < 0.3 else _YELLOW if ratio < 0.6 else _RED
    return {"dimension": "6_redundancy", "band": band, "points": band_points(band),
            "raw": {"property_fragments": total, "unique": unique,
                    "redundancy_ratio": round(ratio, 2)},
            "label": "Reasoned numbers, Sourced direction (SEP-1576)"}


def _percentile(values: list[int], pct: float) -> float:
    if not values:
        return 0.0
    s = sorted(values)
    k = (len(s) - 1) * (pct / 100)
    lo = int(k)
    hi = min(lo + 1, len(s) - 1)
    return s[lo] + (s[hi] - s[lo]) * (k - lo)
