"""FastAPI backend — the synchronous /analyze contract from the diagram.

  POST /analyze            -> 200 {image_url, traits, label}   (does the whole chain)
  GET  /files/{name}       -> the generated image (local storage only)
  GET  /health             -> liveness

The Next.js frontend calls POST /analyze with {answers} and renders the response.
Pass ?include_prompt=true to also get the built prompt back (handy while tuning).

Note: this awaits image generation inline, so keep your reverse-proxy/client
timeouts >= PORTRAIT_GENERATION_TIMEOUT_S. gpt-image-1-mini is the fast/cheap tier,
which is why a synchronous endpoint is viable here.
"""
from __future__ import annotations

import asyncio
import os
import uuid

from fastapi import FastAPI, HTTPException, Query
from fastapi.staticfiles import StaticFiles

from app.analysis.pipeline import analyze
from app.config import settings
from app.generation.base import GenerationError, ImageGenerator, ModerationRejected
from app.generation.fake import FakeImageGenerator
from app.models import AnalyzeRequest, AnalyzeResponse
from app.storage.base import Storage
from app.storage.local import LocalStorage


def _build_generator() -> ImageGenerator:
    if settings.generator == "openai":
        from app.generation.openai_client import OpenAIImageGenerator

        return OpenAIImageGenerator(settings)
    return FakeImageGenerator()


def _build_storage() -> Storage:
    return LocalStorage(settings.storage_dir, settings.base_url)


app = FastAPI(title="Portrait Service")

generator = _build_generator()
storage = _build_storage()

os.makedirs(settings.storage_dir, exist_ok=True)
app.mount("/files", StaticFiles(directory=settings.storage_dir), name="files")


@app.get("/health")
async def health() -> dict:
    return {"status": "ok", "generator": settings.generator}


@app.post("/analyze", response_model=AnalyzeResponse)
async def analyze_endpoint(
    request: AnalyzeRequest,
    include_prompt: bool = Query(default=False),
) -> AnalyzeResponse:
    job_id = uuid.uuid4().hex
    try:
        return await asyncio.wait_for(
            analyze(
                request,
                generator=generator,
                storage=storage,
                job_id=job_id,
                include_prompt=include_prompt,
            ),
            timeout=settings.generation_timeout_s,
        )
    except ModerationRejected as err:
        # the image model's safety filter refused the prompt
        raise HTTPException(status_code=422, detail=f"prompt rejected: {err}")
    except asyncio.TimeoutError:
        raise HTTPException(status_code=504, detail="image generation timed out")
    except GenerationError as err:
        raise HTTPException(status_code=502, detail=f"generation failed: {err}")
