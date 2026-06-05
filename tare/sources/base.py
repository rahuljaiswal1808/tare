from __future__ import annotations

from abc import ABC, abstractmethod

from ..models import ServerConfig, ServerToolset


class ToolSource(ABC):
    @abstractmethod
    def fetch(self, config: ServerConfig) -> ServerToolset:
        ...
