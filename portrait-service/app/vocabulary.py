"""Interest catalog — the closed set of visual motifs the prompt builder can draw
from. Traits.interests holds ids from here; the prompt builder looks each one up
and injects its `description` as an element surrounding the central figure.

Because it's a registry, scoring can only ever reference motifs that actually
exist — no free-text leakage into the prompt. Descriptions are written in English
(the image model responds best to English) and as concrete, paintable scenes so
the final portrait carries real content from the user's answers, not just a color.

Ids here are referenced by app/analysis/trait_scorer.py (the SCORING dict).
"""
from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class Interest:
    id: str
    category: str  # loose grouping: environment | time | sport | music | emotion | trait
    description: str  # the exact phrase injected into the image prompt


INTERESTS: dict[str, Interest] = {
    it.id: it
    for it in [
        # ---- environments (Q1b: where you feel most free) -------------------
        Interest("mountain_peak", "environment",
                 "towering mountain peaks and rolling ranges stretching to the horizon"),
        Interest("sea_edge", "environment",
                 "the edge of a vast sea, rolling waves and sea spray"),
        Interest("dense_forest", "environment",
                 "a deep, dense forest of tall trees and dappled green light"),
        Interest("open_field", "environment",
                 "a wide open field with nothing but grass and sky to the horizon"),

        # ---- times / sky moods (Q1a: what charges you in nature) ------------
        Interest("sunrise", "time",
                 "a soft golden sunrise breaking over the landscape"),
        Interest("storm", "time",
                 "a dramatic storm sky, charged clouds and distant lightning"),
        Interest("starry_night", "time",
                 "a vast starry night sky, constellations and the Milky Way overhead"),
        Interest("sunset", "time",
                 "a warm glowing sunset, amber and rose light spilling across the sky"),

        # ---- how you are in nature (Q1c) ------------------------------------
        Interest("stillness", "trait",
                 "a calm, still atmosphere of quiet contemplation"),
        Interest("exploration", "trait",
                 "a sense of motion and exploration, a path leading onward"),
        Interest("introspection", "trait",
                 "a dreamy, inward, thoughtful atmosphere"),
        Interest("companionship", "trait",
                 "a second, distant abstract figure suggesting shared company"),

        # ---- sport: how you move (Q2a) --------------------------------------
        Interest("solo_training", "sport",
                 "solo training motifs — running shoes and a lone athletic figure in motion"),
        Interest("team_sport", "sport",
                 "team-sport energy — a football and dynamic motion of the game"),
        Interest("outdoor_sport", "sport",
                 "outdoor athletic motifs — hiking trails, a bicycle, open water for swimming"),
        Interest("free_movement", "sport",
                 "free, flowing movement — dance and yoga, fluid expressive lines"),

        # ---- sport: what you seek / how you feel (Q2b, Q2c) -----------------
        Interest("calm_focus", "emotion", "a centered, meditative calm"),
        Interest("ambition", "trait", "an upward, striving, determined energy"),
        Interest("adrenaline", "trait", "a surge of adrenaline, sharp dynamic energy"),
        Interest("embodiment", "trait", "a strong, grounded sense of physical presence"),

        # ---- chaos / unpredictability (Q3) ----------------------------------
        Interest("wandering", "trait",
                 "an open road or drifting path with no fixed destination"),
        Interest("discovery", "trait", "doorways and openings hinting at the unknown"),
        Interest("spontaneity", "trait", "loose, spontaneous, unplanned composition"),
        Interest("fluidity", "trait", "flowing, shifting, ever-changing forms"),
        Interest("energy_burst", "trait",
                 "bursts of swirling abstract energy radiating outward"),
        Interest("detachment", "trait", "a calm, detached, observing distance"),
        Interest("surrender", "trait", "soft dissolving forms, a sense of letting go"),

        # ---- emotions (Q4) --------------------------------------------------
        Interest("nostalgia", "emotion",
                 "a warm nostalgic haze, faded photo tones and soft memory light"),
        Interest("longing", "emotion",
                 "a wistful sense of longing and quiet distance"),
        Interest("spark", "emotion",
                 "bright sparks of enthusiasm and curiosity scattered through the scene"),
        Interest("melancholy", "emotion",
                 "a beautiful melancholy, gentle and bittersweet"),
        Interest("creativity", "trait",
                 "creative motifs — drifting ink, brushstrokes and forming shapes"),
        Interest("human_connection", "emotion",
                 "small, sincere human gestures and warmth between figures"),
        Interest("beauty", "emotion", "an emphasis on delicate, striking natural beauty"),
        Interest("ideas", "trait",
                 "floating geometric ideas and lines of thought, like a constellation of concepts"),

        # ---- music (Q5) -----------------------------------------------------
        Interest("music_notes", "music",
                 "musical notes and soft visible sound waves drifting through the air"),
        Interest("acoustic_warmth", "music",
                 "warm analog music motifs — soft strings, vinyl warmth, gentle indie-folk tones"),
        Interest("electric_energy", "music",
                 "intense electric music motifs — neon soundwaves, bold rhythmic pulses"),
        Interest("varied_rhythm", "music",
                 "an eclectic mix of musical motifs in shifting colors and rhythms"),
        Interest("dance", "music", "a body caught mid-dance, fluid rhythmic motion"),
        Interest("immersion", "music",
                 "an enveloping, immersive wash of sound and color"),
    ]
}


def describe(interest_ids: list[str]) -> list[str]:
    """Resolve catalog ids to prompt descriptions, skipping unknown ids."""
    return [INTERESTS[i].description for i in interest_ids if i in INTERESTS]
