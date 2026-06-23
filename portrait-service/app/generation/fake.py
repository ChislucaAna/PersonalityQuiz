"""Fake image generator for local dev and tests.

Produces a real PNG whose colors are derived deterministically from the prompt,
so the same prompt yields the same image — handy for testing the pipeline without
spending money or needing network access. It draws nothing meaningful; it just
proves the end-to-end path (profile -> prompt -> bytes -> storage -> url) works.
"""
from __future__ import annotations

import asyncio
import hashlib
import io

from PIL import Image, ImageDraw


def _color_from(seed: str, salt: str) -> tuple[int, int, int]:
    h = hashlib.sha256((salt + seed).encode()).hexdigest()
    return int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16)


class FakeImageGenerator:
    def __init__(self, size: tuple[int, int] = (512, 768)) -> None:
        self.size = size  # small + portrait-ish; just for local speed

    async def generate(self, prompt: str) -> bytes:
        return await asyncio.to_thread(self._render, prompt)

    def _render(self, prompt: str) -> bytes:
        w, h = self.size
        top = _color_from(prompt, "top")
        bottom = _color_from(prompt, "bottom")
        img = Image.new("RGB", (w, h))
        draw = ImageDraw.Draw(img)
        # simple vertical gradient between two prompt-derived colors
        for y in range(h):
            t = y / max(h - 1, 1)
            row = tuple(int(top[i] * (1 - t) + bottom[i] * t) for i in range(3))
            draw.line([(0, y), (w, y)], fill=row)
        buf = io.BytesIO()
        img.save(buf, format="PNG")
        return buf.getvalue()
