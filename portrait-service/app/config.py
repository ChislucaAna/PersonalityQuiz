"""Runtime configuration.

Backends are swappable by env var so the same code runs locally (fake image
generator, local disk) and in production (OpenAI, object storage) with no code
changes.
"""
from __future__ import annotations

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_prefix="PORTRAIT_")

    # public base URL the service is reached at (used to build image URLs)
    base_url: str = "http://localhost:8000"

    # which image backend: "fake" (local, no API key) or "openai"
    generator: str = "fake"

    # storage backend: "local" (disk) — swap for s3/gcs later
    storage: str = "local"
    storage_dir: str = "./_data/images"

    # how many interest motifs to carry into a single prompt
    max_motifs: int = 4

    # hard ceiling on a single generation, in seconds (synchronous endpoint)
    generation_timeout_s: float = 120.0

    # OpenAI image settings (only used when generator == "openai")
    openai_api_key: str = "none"
    # gpt-image-1-mini per the diagram; also gpt-image-1 | gpt-image-1.5
    openai_model: str = "gpt-image-1-mini"
    # portrait orientation; one of 1024x1024 | 1536x1024 | 1024x1536
    openai_size: str = "1024x1536"
    openai_quality: str = "high"   # low | medium | high
    openai_moderation: str = "auto"  # auto | low


settings = Settings()
