#!/usr/bin/env python3
"""Capture a live tools/list response to a manifest file.

Usage:
    # HTTP server (token from env):
    GITHUB_MCP_TOKEN=<tok> python scripts/capture_manifest.py \
        --config servers.toml --server github --out manifests/github.json

    # Or use the tare CLI live path directly; this script is a thin helper
    # that also writes the raw manifest JSON.
"""
from __future__ import annotations

import argparse
import asyncio
import json
import os
import sys
import tomllib
from datetime import datetime, timezone
from pathlib import Path

# Allow running from repo root without install
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from tare.models import ServerConfig


async def fetch_tools(cfg: ServerConfig) -> list[dict]:
    from mcp import ClientSession

    if cfg.transport == "http":
        from mcp.client.streamable_http import streamablehttp_client

        headers: dict[str, str] = {}
        if cfg.auth_env:
            token = os.environ.get(cfg.auth_env, "")
            if token:
                headers["Authorization"] = f"Bearer {token}"
            else:
                print(f"WARNING: {cfg.auth_env} is not set; request will likely be rejected", file=sys.stderr)

        async with streamablehttp_client(cfg.url, headers=headers) as (read, write, _):
            async with ClientSession(read, write) as session:
                await session.initialize()
                result = await session.list_tools()

    elif cfg.transport == "stdio":
        from mcp.client.stdio import StdioServerParameters, stdio_client

        params = StdioServerParameters(command=cfg.command[0], args=cfg.command[1:])
        async with stdio_client(params) as (read, write):
            async with ClientSession(read, write) as session:
                await session.initialize()
                result = await session.list_tools()
    else:
        raise ValueError(f"unsupported transport: {cfg.transport}")

    return [t.model_dump(by_alias=True) for t in result.tools]


def main():
    ap = argparse.ArgumentParser(description="Capture MCP tools/list to a manifest JSON.")
    ap.add_argument("--config", default="servers.toml")
    ap.add_argument("--server", required=True)
    ap.add_argument("--out", required=True, help="Path to write manifest JSON")
    args = ap.parse_args()

    data = tomllib.loads(Path(args.config).read_text())
    servers = {name: ServerConfig(name=name, **cfg) for name, cfg in data.get("server", {}).items()}
    if args.server not in servers:
        print(f"ERROR: server '{args.server}' not in {args.config}", file=sys.stderr)
        sys.exit(1)

    cfg = servers[args.server]
    print(f"Fetching tools/list from {cfg.name} ({cfg.transport}: {cfg.url or cfg.command}) ...")
    tools = asyncio.run(fetch_tools(cfg))
    print(f"Got {len(tools)} tools.")

    manifest = {
        "captured_at": datetime.now(timezone.utc).isoformat(),
        "provenance": f"live:{cfg.transport}:{cfg.url or cfg.command}",
        "declares_dynamic_toolsets": cfg.declares_dynamic_toolsets,
        "tools": tools,
    }

    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(manifest, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"Written to {out}")


if __name__ == "__main__":
    main()
