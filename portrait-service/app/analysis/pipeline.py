r"""Analyze pipeline — chains the diagram's boxes in order.

answers -> trait scorer -> style config -> prompt builder -> OpenAI -> storage
                       \-> labeler ----------------------------------/

Returns the assembled AnalyzeResponse. Synchronous: the caller awaits the whole
chain and gets {image_url, traits, label} back in one response.
"""
from __future__ import annotations

from app.analysis.labeler import make_label
from app.analysis.prompt_builder import build_prompt
from app.analysis.style_config import configure_style
from app.analysis.trait_scorer import SCORING, score_traits
from app.config import settings
from app.generation.base import GenerationError, ImageGenerator
from app.models import AnalyzeRequest, AnalyzeResponse
from app.storage.base import Storage


async def analyze(
    request: AnalyzeRequest,
    *,
    generator: ImageGenerator,
    storage: Storage,
    job_id: str,
    include_prompt: bool = False,
) -> AnalyzeResponse:
    traits = score_traits(request.answers, SCORING)
    style = configure_style(traits, max_motifs=settings.max_motifs)
    label = make_label(traits)
    prompt = build_prompt(style)

    image_bytes = await generator.generate(prompt)
    # sanity check: never persist or serve an empty/failed generation
    if not image_bytes:
        raise GenerationError("generator returned no image bytes")
    image_url = await storage.save(f"{job_id}.png", image_bytes, "image/png")

    return AnalyzeResponse(
        image_url=image_url,
        traits=traits,
        label=label,
        style=style,
        prompt=prompt if include_prompt else None,
    )
