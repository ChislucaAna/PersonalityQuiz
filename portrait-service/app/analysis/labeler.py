"""Labeler  —  produces the shareable archetype ('label' in the response).

Rule-based and deterministic: the first matching archetype wins, so ordering is the
priority. Falls back to a neutral archetype when nothing matches. This is the bit
users screenshot and share, so it's worth tuning the names/blurbs once the real
quiz exists.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Callable

from app.models import Label, Traits

HI = 0.66
LO = 0.34


@dataclass(frozen=True)
class Archetype:
    name: str
    blurb: str
    matches: Callable[[dict[str, float]], bool]


_ARCHETYPES: list[Archetype] = [
    Archetype(
        "The Dreamer",
        "Head among the stars, forever chasing the next idea.",
        lambda s: s["openness"] >= HI and s["energy"] <= LO,
    ),
    Archetype(
        "The Explorer",
        "Restless, curious, and happiest in motion.",
        lambda s: s["openness"] >= HI and s["energy"] >= HI,
    ),
    Archetype(
        "The Firebrand",
        "Bold, vivid, and impossible to ignore.",
        lambda s: s["intensity"] >= HI and s["energy"] >= HI,
    ),
    Archetype(
        "The Naturalist",
        "Grounded, calm, and quietly tuned to the world outside.",
        lambda s: s["nature_affinity"] >= HI and s["energy"] <= LO,
    ),
    Archetype(
        "The Warm Heart",
        "Easy company, generous with attention and warmth.",
        lambda s: s["warmth"] >= HI,
    ),
    Archetype(
        "The Quiet Observer",
        "Reserved, perceptive, and comfortable in the background.",
        lambda s: s["energy"] <= LO and s["intensity"] <= LO,
    ),
]

_FALLBACK = Archetype(
    "The Original",
    "A blend all your own — hard to pin down, easy to remember.",
    lambda s: True,
)


def make_label(traits: Traits) -> Label:
    for arch in _ARCHETYPES:
        if arch.matches(traits.scores):
            return Label(name=arch.name, blurb=arch.blurb)
    return Label(name=_FALLBACK.name, blurb=_FALLBACK.blurb)
