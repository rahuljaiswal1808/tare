"""Data models for TARE."""
from __future__ import annotations

from datetime import datetime
from typing import Any, Optional

from pydantic import BaseModel, Field


class Tool(BaseModel):
    name: str
    description: Optional[str] = None
    input_schema: dict[str, Any] = Field(default_factory=dict, alias="inputSchema")
    output_schema: Optional[dict[str, Any]] = Field(default=None, alias="outputSchema")

    model_config = {"populate_by_name": True, "extra": "allow"}


class ServerToolset(BaseModel):
    server: str
    source_kind: str  # "live" | "manifest"
    captured_at: datetime
    provenance: str = ""
    declares_dynamic_toolsets: bool = False
    tools: list[Tool] = Field(default_factory=list)


class ServerConfig(BaseModel):
    name: str
    transport: str = "none"  # "http" | "stdio" | "none"
    url: Optional[str] = None
    command: Optional[list[str]] = None
    auth_env: Optional[str] = None  # env var holding a bearer token
    manifest_path: Optional[str] = None
    declares_dynamic_toolsets: bool = False
    notes: str = ""
