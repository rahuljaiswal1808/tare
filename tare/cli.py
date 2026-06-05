"""TARE command line interface."""
from __future__ import annotations

import json
import tomllib
from pathlib import Path

import typer
from rich.console import Console

from .models import ServerConfig
from .report import leaderboard_markdown, load_results
from .scoring import measure
from .sources import LiveMCPSource, ManifestSource
from .tokenizer import REFERENCE_ENCODING, Tokenizer

app = typer.Typer(add_completion=False, help="Tool And Response Economy benchmark harness.")
console = Console()


def _load_configs(path: str) -> dict[str, ServerConfig]:
    data = tomllib.loads(Path(path).read_text(encoding="utf-8"))
    return {name: ServerConfig(name=name, **cfg) for name, cfg in data.get("server", {}).items()}


def _fetch(cfg: ServerConfig, source: str):
    """source: live | manifest | auto. auto tries live, then manifest."""
    if source == "live":
        return LiveMCPSource().fetch(cfg)
    if source == "manifest":
        return ManifestSource().fetch(cfg)
    # auto
    try:
        return LiveMCPSource().fetch(cfg)
    except Exception as exc:  # noqa: BLE001
        console.print(f"[yellow]{cfg.name}: live fetch failed ({exc}); falling back to manifest[/]")
        return ManifestSource().fetch(cfg)


@app.command()
def measure_server(
    server: str = typer.Option(..., "--server", help="Server name from servers.toml, or 'all'."),
    config: str = typer.Option("servers.toml", "--config"),
    source: str = typer.Option("auto", "--source", help="live | manifest | auto"),
    tokenizer: str = typer.Option(REFERENCE_ENCODING, "--tokenizer", help=f"{REFERENCE_ENCODING} | approx"),
    out_dir: str = typer.Option("results", "--out"),
):
    """Measure one server (or all) and write a result JSON per server."""
    configs = _load_configs(config)
    tok = Tokenizer(tokenizer)
    if not tok.is_reference:
        console.print("[yellow]Using approx tokenizer: results are smoke-test only.[/]")
    Path(out_dir).mkdir(parents=True, exist_ok=True)

    targets = list(configs.values()) if server == "all" else [configs[server]]
    for cfg in targets:
        try:
            ts = _fetch(cfg, source)
        except Exception as exc:  # noqa: BLE001
            console.print(f"[red]{cfg.name}: skipped ({exc})[/]")
            continue
        result = measure(ts, tok)
        Path(out_dir, f"{cfg.name}.json").write_text(json.dumps(result, indent=2), encoding="utf-8")
        console.print(
            f"[green]{cfg.name}[/]: score={result['design_score']} "
            f"cost={result['static_context_cost']:,} tools={result['tool_count']} "
            f"({result['source_kind']})"
        )


@app.command()
def report(
    results_dir: str = typer.Option("results", "--results"),
    out: str = typer.Option("results/LEADERBOARD.md", "--out"),
):
    """Build the leaderboard markdown from result JSON files."""
    results = load_results(results_dir)
    if not results:
        console.print("[red]no results found; run measure-server first[/]")
        raise typer.Exit(1)
    md = leaderboard_markdown(results)
    Path(out).write_text(md, encoding="utf-8")
    console.print(md)
    console.print(f"\n[green]written to {out}[/]")


if __name__ == "__main__":
    app()
