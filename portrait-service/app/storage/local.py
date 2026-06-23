"""Local-disk storage. Files are served by FastAPI's StaticFiles mount at /files.

Production swap: replace with an implementation that uploads to object storage and
returns the CDN/object URL. The pipeline never changes.
"""
from __future__ import annotations

import asyncio
import os


class LocalStorage:
    def __init__(self, directory: str, base_url: str) -> None:
        self._dir = directory
        self._base_url = base_url.rstrip("/")
        os.makedirs(self._dir, exist_ok=True)

    async def save(self, name: str, data: bytes, content_type: str) -> str:
        if not data:
            raise ValueError("refusing to save empty image data")
        path = os.path.join(self._dir, name)
        await asyncio.to_thread(self._write, path, data)
        return f"{self._base_url}/files/{name}"

    @staticmethod
    def _write(path: str, data: bytes) -> None:
        with open(path, "wb") as fh:
            fh.write(data)
        # sanity check: the file must exist and match the bytes we were given
        written = os.path.getsize(path)
        if written != len(data):
            raise IOError(
                f"storage wrote {written} bytes but expected {len(data)} for {path}"
            )
