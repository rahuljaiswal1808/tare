import json
from pathlib import Path

from tare.models import ServerToolset, Tool
from tare.scoring import measure
from tare.tokenizer import Tokenizer


def _fixture_toolset() -> ServerToolset:
    data = json.loads(Path("manifests/fixture.json").read_text())
    return ServerToolset(
        server="fixture", source_kind="manifest",
        captured_at="2026-06-05T00:00:00+00:00",
        tools=[Tool.model_validate(t) for t in data["tools"]],
        declares_dynamic_toolsets=data["declares_dynamic_toolsets"],
    )


def test_measure_produces_headline_figures():
    ts = _fixture_toolset()
    tok = Tokenizer("approx")
    result = measure(ts, tok)
    assert 0 <= result["design_score"] <= 100
    assert result["static_context_cost"] > 0
    assert result["tool_count"] == 4
    assert set(result["dimensions"]) == {
        "1_tool_surface", "2_schema_footprint", "3_progressive_disclosure",
        "4_response_discipline", "5_description_quality", "6_redundancy",
    }


def test_small_server_has_green_surface():
    ts = _fixture_toolset()
    result = measure(ts, Tokenizer("approx"))
    assert result["dimensions"]["1_tool_surface"]["band"] == "green"


def test_response_discipline_detects_shaping():
    ts = _fixture_toolset()
    result = measure(ts, Tokenizer("approx"))
    # list_issues and search_code expose limit/page/cursor; get_issue/create_issue do not
    assert result["dimensions"]["4_response_discipline"]["raw"]["data_tools"] >= 2
