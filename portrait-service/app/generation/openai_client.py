"""OpenAI image generator — supports both model families with one code path.

Encodes the real constraints of the OpenAI image API:
  * No seed parameter exists — reproducibility lives entirely in the prompt.
  * Both families return base64 (we decode to bytes; storage hosts the file).
  * Model-family differences are handled here:
      - dall-e-*  : needs response_format="b64_json", quality "standard"/"hd",
                    does NOT accept a `moderation` parameter. Works with just an
                    API key (no organization verification).
      - gpt-image-*: returns b64 by default (no response_format), accepts a
                    `moderation` parameter, quality "low"/"medium"/"high".
                    Requires organization verification on the OpenAI account.
  * The moderation filter can refuse a prompt -> surfaced as ModerationRejected.
  * Org-verification refusals are surfaced with an actionable message.
  * The blocking SDK call is pushed to a thread so it doesn't stall the loop.

Output is sanity-checked before returning: the response must contain decodable
base64 that is a real PNG/JPEG/WebP image of non-trivial size.
"""
from __future__ import annotations

import asyncio
import base64

from app.config import Settings
from app.generation.base import GenerationError, ModerationRejected

# substrings (lowercased) that identify each error class in SDK exception text
_MODERATION_NEEDLES = (
    "moderation", "safety system", "content policy", "rejected", "blocked",
    "flagged", "safety",
)
_VERIFICATION_NEEDLES = (
    "must be verified", "organization verification", "verify your organization",
    "to use the model", "verification", "does not have access", "not have access",
)


def _has(text: str, needles: tuple[str, ...]) -> bool:
    return any(n in text for n in needles)


def _looks_like_image(raw: bytes) -> bool:
    """Cheap magic-byte check for the formats the image API can return."""
    if len(raw) < 100:  # a real image is never this tiny
        return False
    if raw[:8] == b"\x89PNG\r\n\x1a\n":          # PNG
        return True
    if raw[:3] == b"\xff\xd8\xff":               # JPEG
        return True
    if raw[:4] == b"RIFF" and raw[8:12] == b"WEBP":  # WebP
        return True
    return False


def _key_is_set(key: str) -> bool:
    return bool(key) and key.strip().lower() != "none"


class OpenAIImageGenerator:
    def __init__(self, settings: Settings) -> None:
        if not _key_is_set(settings.openai_api_key):
            raise GenerationError("PORTRAIT_OPENAI_API_KEY is not set")
        # imported lazily so the package is optional when using the fake backend
        from openai import OpenAI

        self._client = OpenAI(api_key=settings.openai_api_key)
        self._model = settings.openai_model
        self._size = settings.openai_size
        self._quality = settings.openai_quality
        self._moderation = settings.openai_moderation
        self._is_gpt_image = self._model.startswith("gpt-image")

    async def generate(self, prompt: str) -> bytes:
        return await asyncio.to_thread(self._generate_sync, prompt)

    def _build_kwargs(self, prompt: str) -> dict:
        kwargs: dict = {"model": self._model, "prompt": prompt, "size": self._size, "n": 1}
        if self._is_gpt_image:
            # gpt-image: b64 by default; supports moderation; quality low|medium|high
            kwargs["quality"] = self._quality
            kwargs["moderation"] = self._moderation
        else:
            # dall-e: must request b64; quality only standard|hd; no moderation param
            kwargs["response_format"] = "b64_json"
            if self._quality in ("standard", "hd"):
                kwargs["quality"] = self._quality
        return kwargs

    def _generate_sync(self, prompt: str) -> bytes:
        try:
            resp = self._client.images.generate(**self._build_kwargs(prompt))
        except Exception as err:  # noqa: BLE001 - normalize SDK errors
            text = str(err).lower()
            # verification first: its messages can also contain generic words
            if _has(text, _VERIFICATION_NEEDLES) and "moderation" not in text:
                raise GenerationError(
                    "OpenAI refused the request because this model needs organization "
                    "verification. Either verify your org at platform.openai.com "
                    "(Settings -> Organization), or set PORTRAIT_OPENAI_MODEL=dall-e-3, "
                    "which works with just an API key. "
                    f"Original error: {err}"
                ) from err
            if _has(text, _MODERATION_NEEDLES):
                raise ModerationRejected(str(err)) from err
            raise GenerationError(str(err)) from err

        return self._extract_image(resp)

    # ---- output sanity checks ------------------------------------------- #
    @staticmethod
    def _extract_image(resp) -> bytes:
        data = getattr(resp, "data", None)
        if not data:
            raise GenerationError("OpenAI returned an empty response (no image data).")

        first = data[0]
        b64 = getattr(first, "b64_json", None)
        if not b64:
            # dall-e with response_format=url, or an unexpected shape
            url = getattr(first, "url", None)
            if url:
                raise GenerationError(
                    "OpenAI returned an image URL instead of base64 data. "
                    "Ensure response_format='b64_json' (dall-e) is requested."
                )
            raise GenerationError("OpenAI response contained no base64 image data.")

        try:
            raw = base64.b64decode(b64)
        except Exception as err:  # noqa: BLE001
            raise GenerationError(f"Could not decode the returned base64 image: {err}") from err

        if not _looks_like_image(raw):
            raise GenerationError(
                f"Decoded data is not a valid image (got {len(raw)} bytes, "
                "no PNG/JPEG/WebP signature)."
            )
        return raw
