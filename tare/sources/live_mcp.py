"""Live source: connect to a running MCP server and call tools/list.

Authoritative path. Requires the optional 'mcp' dependency (pip install 'tare[live]')
and, for most SaaS servers, a bearer token supplied via the configured auth_env.

NOTE for Claude Code: verify the exact mcp SDK call signatures against the installed
version. The protocol is stable but the Python SDK's client helpers have moved between
releases (transport import paths, list_tools() return shape). The shape below targets
mcp >= 1.2 with Streamable HTTP and stdio transports.
"""
from __future__ import annotations

import asyncio
import os
from datetime import datetime, timezone

from ..models import ServerConfig, ServerToolset, Tool
from .base import ToolSource


class LiveMCPSource(ToolSource):
    def fetch(self, config: ServerConfig) -> ServerToolset:
        return asyncio.run(self._fetch_async(config))

    async def _fetch_async(self, config: ServerConfig) -> ServerToolset:
        try:
            from mcp import ClientSession
        except ImportError as exc:
            raise RuntimeError(
                "live source needs the mcp package: pip install 'tare[live]'"
            ) from exc

        if config.transport == "http":
            from mcp.client.streamable_http import streamablehttp_client

            headers = {}
            if config.auth_env:
                token = os.environ.get(config.auth_env)
                if token:
                    headers["Authorization"] = f"Bearer {token}"
            async with streamablehttp_client(config.url, headers=headers) as (read, write, _):
                async with ClientSession(read, write) as session:
                    await session.initialize()
                    result = await session.list_tools()
        elif config.transport == "stdio":
            from mcp.client.stdio import StdioServerParameters, stdio_client

            if not config.command:
                raise ValueError(f"{config.name}: stdio transport needs a command")
            params = StdioServerParameters(command=config.command[0], args=config.command[1:])
            async with stdio_client(params) as (read, write):
                async with ClientSession(read, write) as session:
                    await session.initialize()
                    result = await session.list_tools()
        else:
            raise ValueError(
                f"{config.name}: transport '{config.transport}' is not live-fetchable"
            )

        tools = [Tool.model_validate(t.model_dump(by_alias=True)) for t in result.tools]
        return ServerToolset(
            server=config.name,
            source_kind="live",
            captured_at=datetime.now(timezone.utc),
            provenance=f"live:{config.transport}:{config.url or config.command}",
            declares_dynamic_toolsets=config.declares_dynamic_toolsets,
            tools=tools,
        )
