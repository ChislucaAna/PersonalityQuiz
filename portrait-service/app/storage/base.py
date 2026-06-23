"""Storage interface.

Receives image bytes, persists them somewhere, returns a public URL. Swap
LocalStorage for an S3/GCS implementation without touching the pipeline.
"""
from __future__ import annotations

from typing import Protocol


class Storage(Protocol):
    async def save(self, name: str, data: bytes, content_type: str) -> str:
        """Persist `data` and return a URL the client can fetch it from."""
        ...
