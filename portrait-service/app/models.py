"""Data models, named to match the architecture diagram.

Flow:  answers --(trait scorer)--> Traits --(style config)--> Style
       Style --(prompt builder)--> prompt --(OpenAI)--> image
       Traits --(labeler)--> Label

The /analyze endpoint is synchronous and returns {image_url, traits, label}.
"""
from __future__ import annotations

from enum import Enum

from pydantic import BaseModel, Field


# ----------------------------- vocabularies ------------------------------- #
# Closed enums for the structural style fields: fully inspectable and testable.
class Palette(str, Enum):
    warm = "warm"
    cool = "cool"
    muted = "muted"
    vibrant = "vibrant"
    monochrome = "monochrome"


class ArtStyle(str, Enum):
    painterly = "painterly"
    geometric = "geometric"
    dreamy = "dreamy"
    minimal = "minimal"
    bold_graphic = "bold_graphic"


class Mood(str, Enum):
    serene = "serene"
    playful = "playful"
    intense = "intense"
    melancholic = "melancholic"
    whimsical = "whimsical"


class Setting(str, Enum):
    studio = "studio"
    nature = "nature"
    cosmic = "cosmic"
    urban = "urban"
    abstract = "abstract"


class Figure(str, Enum):
    none = "none"
    silhouette = "silhouette"
    stylized_character = "stylized_character"


# The continuous trait axes the scorer produces. Each is a 0..1 score.
# Quiz-agnostic on purpose — the real quiz just needs to push these.
TRAIT_AXES = ("energy", "warmth", "openness", "intensity", "nature_affinity")


# ------------------------------- request ---------------------------------- #
class Answer(BaseModel):
    question_id: str
    answer_id: str


class AnalyzeRequest(BaseModel):
    answers: list[Answer] = Field(min_length=1)


# --------------------- intermediate + response shapes --------------------- #
class Traits(BaseModel):
    """Output of the trait scorer."""
    scores: dict[str, float]   # axis -> 0..1
    interests: list[str]       # interest/hobby tag ids (from the catalog)


class Style(BaseModel):
    """Output of the style config (traits -> art style)."""
    palette: Palette
    art_style: ArtStyle
    mood: Mood
    setting: Setting
    figure: Figure
    motifs: list[str]


class Label(BaseModel):
    """Output of the labeler — the shareable archetype."""
    name: str
    blurb: str


class AnalyzeResponse(BaseModel):
    image_url: str
    traits: Traits
    label: Label
    # extra, harmless-to-ignore fields for transparency/debugging:
    style: Style | None = None
    prompt: str | None = None
