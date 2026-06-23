r"""Prompt builder  —  the "Traits -> image prompt" box.

Takes the resolved Style and produces a strict, structured prompt. The portrait
ALWAYS centers a single faceless, featureless human figure (no facial features),
surrounded by the concrete motifs the user's answers selected — so the image reads
as "this is me, and these are the things that make up my world," never just a flat
color wash.

The structure is fixed; the style fills the slots and the interests are injected as
the elements arranged around the figure. Deterministic on purpose: with no seed on
the OpenAI side, the prompt is the only lever you control, so it's the thing worth
testing.
"""
from __future__ import annotations

from app.models import Style
from app.vocabulary import describe

# How the central figure is rendered, varied by the resolved Figure value. Every
# variant is a faceless, featureless human — only the rendering style changes.
_FIGURE_RENDER = {
    "none": "rendered as a soft, semi-abstract form",
    "silhouette": "rendered as a clean dark silhouette",
    "stylized_character": "rendered as a stylized, illustrated, non-photoreal character",
}


def build_prompt(style: Style) -> str:
    figure_render = _FIGURE_RENDER.get(style.figure.value, _FIGURE_RENDER["none"])

    elements = describe(style.motifs)
    if elements:
        elements_line = (
            "Surround the figure with these elements, woven into one cohesive scene: "
            + "; ".join(elements)
            + "."
        )
    else:
        elements_line = "Keep the surrounding scene clean, symbolic, and uncluttered."

    return "\n".join(
        [
            # --- the subject: always a faceless, anonymous human figure ---
            f"A {style.art_style.value} symbolic portrait. At the very center stands a "
            f"single faceless, featureless human figure — a smooth, blank face with no "
            f"eyes, nose, or mouth — gender-neutral and anonymous, "
            f"{figure_render}. The figure represents the viewer.",
            # --- the world built from their answers ---
            elements_line,
            f"Scenery and setting: {style.setting.value}.",
            f"Overall color palette: {style.palette.value}.",
            f"Mood and atmosphere: {style.mood.value}.",
            # --- hard constraints ---
            "Composition: a single cohesive, balanced scene in portrait orientation, "
            "the figure clearly the focal point, surrounded by the elements above. "
            "Expressive, tasteful, evocative. "
            "Absolutely no facial features on the figure. "
            "No text, no lettering, no words, no watermark, no logos.",
        ]
    )
