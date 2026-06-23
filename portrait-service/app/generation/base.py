"""Image-generation interface.

Anything that turns a prompt into PNG bytes implements `ImageGenerator`. The rest
of the pipeline only knows this interface, so swapping fake <-> OpenAI <-> anything
else is a config change, never a code change.
"""
from __future__ import annotations

from typing import Protocol


class GenerationError(Exception):
    """A generation attempt failed for a non-content reason (network, quota, bug)."""


class ModerationRejected(Exception):
    """The image model's safety filter refused the prompt.

    Mapped to the job's `rejected` state so the UI can show a graceful message
    instead of a generic error.
    """


class ImageGenerator(Protocol):
    async def generate(self, prompt: str) -> bytes:
        """Return PNG image bytes for the given prompt."""
        ...
