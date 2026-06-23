"""Style config  —  the "Trait -> art style" box.

Deterministic threshold rules translate the continuous trait scores into the
closed style vocabulary. Keeping this separate from the trait scorer means you can
retune how traits *look* without touching how answers *score* — the two concerns
the diagram deliberately splits.
"""
from __future__ import annotations

from app.models import ArtStyle, Figure, Mood, Palette, Setting, Style, Traits

HI = 0.66
LO = 0.34


def configure_style(traits: Traits, *, max_motifs: int = 4) -> Style:
    s = traits.scores
    energy = s["energy"]
    warmth = s["warmth"]
    openness = s["openness"]
    intensity = s["intensity"]
    nature = s["nature_affinity"]

    return Style(
        palette=_palette(warmth, energy, intensity),
        art_style=_art_style(openness, intensity, warmth),
        mood=_mood(energy, warmth, openness, intensity),
        setting=_setting(nature, energy, openness),
        figure=_figure(openness, intensity),
        motifs=traits.interests[:max_motifs],
    )


def _palette(warmth: float, energy: float, intensity: float) -> Palette:
    if energy >= HI and intensity >= HI:
        return Palette.vibrant
    if warmth >= HI:
        return Palette.warm
    if warmth <= LO:
        return Palette.cool
    if energy <= LO and intensity <= LO:
        return Palette.muted
    return Palette.monochrome


def _art_style(openness: float, intensity: float, warmth: float) -> ArtStyle:
    if openness >= HI:
        return ArtStyle.dreamy
    if intensity >= HI:
        return ArtStyle.bold_graphic
    if openness <= LO and intensity <= LO:
        return ArtStyle.minimal
    if warmth >= HI:
        return ArtStyle.painterly
    return ArtStyle.geometric


def _mood(energy: float, warmth: float, openness: float, intensity: float) -> Mood:
    if energy >= HI and warmth >= HI:
        return Mood.playful
    if energy <= LO and warmth <= LO:
        return Mood.melancholic
    if intensity >= HI:
        return Mood.intense
    if openness >= HI:
        return Mood.whimsical
    return Mood.serene


def _setting(nature: float, energy: float, openness: float) -> Setting:
    if nature >= HI:
        return Setting.nature
    if openness >= HI:
        return Setting.cosmic
    if nature <= LO and energy >= HI:
        return Setting.urban
    if energy <= LO:
        return Setting.studio
    return Setting.abstract


def _figure(openness: float, intensity: float) -> Figure:
    if openness >= HI:
        return Figure.stylized_character
    if intensity <= LO:
        return Figure.silhouette
    return Figure.none
