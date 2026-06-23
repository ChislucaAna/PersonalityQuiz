"""Trait scorer  —  the "Answers -> trait scores" box.

Data-driven: the engine is complete; the *content* (which answer pushes which
trait) lives in SCORING as plain data, so plugging in the real quiz later is
editing a dict, not writing code.

Each trait axis starts at a neutral 0.5 and accumulates signed deltas, clamped to
0..1. Interest tags are collected from answers (deduped, order-stable). The output
is deterministic for a given answer set — important, since the image model has no
seed and reproducibility must come from upstream.
"""
from __future__ import annotations

from collections import defaultdict
from dataclasses import dataclass, field
from typing import Iterable

from app.models import TRAIT_AXES, Answer, Traits

_NEUTRAL = 0.5


@dataclass(frozen=True)
class Scoring:
    # trait axis -> signed delta applied to the 0..1 score
    deltas: dict[str, float] = field(default_factory=dict)
    # interest catalog ids contributed by this answer
    interests: tuple[str, ...] = ()


Key = tuple[str, str]  # (question_id, answer_id)


def score_traits(answers: Iterable[Answer], scoring: dict[Key, Scoring]) -> Traits:
    totals: dict[str, float] = {axis: _NEUTRAL for axis in TRAIT_AXES}
    interests: list[str] = []
    seen: set[str] = set()

    for ans in answers:
        rule = scoring.get((ans.question_id, ans.answer_id))
        if rule is None:
            continue  # unmapped answers simply don't contribute
        for axis, delta in rule.deltas.items():
            if axis in totals:
                totals[axis] += delta
        for interest in rule.interests:
            if interest not in seen:
                seen.add(interest)
                interests.append(interest)

    scores = {axis: round(_clamp(v), 3) for axis, v in totals.items()}
    return Traits(scores=scores, interests=interests)


def _clamp(v: float, lo: float = 0.0, hi: float = 1.0) -> float:
    return max(lo, min(hi, v))


# --------------------------------------------------------------------------- #
# SCORING for the adaptive quiz (see Intrebari.txt).
#
# Keys are (question_id, answer_id):
#   * main questions:  ids "1".."5",  answers "yes" / "no"
#   * follow-ups:      ids like "1a".."5c",  answers "a" / "b" / "c" / "d"
# Follow-ups are only ever answered when the parent main was "yes", so only those
# keys need to exist. Unmapped answers are simply ignored by the engine.
#
# Each entry nudges the trait axes and/or contributes visual motifs (ids from
# app/vocabulary.py). The motifs are what make the final image specific.
# --------------------------------------------------------------------------- #
SCORING: dict[Key, Scoring] = {
    # ===== 1. NATURE / OUTDOOR =============================================
    ("1", "yes"): Scoring(deltas={"nature_affinity": +0.35, "warmth": +0.05}),
    ("1", "no"): Scoring(deltas={"nature_affinity": -0.25, "energy": +0.1}),
    # 1a — what moment in nature charges you
    ("1a", "a"): Scoring(deltas={"warmth": +0.05, "energy": -0.05}, interests=("sunrise",)),
    ("1a", "b"): Scoring(deltas={"intensity": +0.15, "energy": +0.1}, interests=("storm",)),
    ("1a", "c"): Scoring(deltas={"openness": +0.15}, interests=("starry_night",)),
    ("1a", "d"): Scoring(deltas={"warmth": +0.1}, interests=("sunset",)),
    # 1b — where you feel most free
    ("1b", "a"): Scoring(interests=("mountain_peak",)),
    ("1b", "b"): Scoring(interests=("sea_edge",)),
    ("1b", "c"): Scoring(interests=("dense_forest",)),
    ("1b", "d"): Scoring(interests=("open_field",)),
    # 1c — how you are in nature
    ("1c", "a"): Scoring(deltas={"energy": -0.1}, interests=("stillness",)),
    ("1c", "b"): Scoring(deltas={"energy": +0.1, "openness": +0.1}, interests=("exploration",)),
    ("1c", "c"): Scoring(deltas={"openness": +0.05}, interests=("introspection",)),
    ("1c", "d"): Scoring(deltas={"warmth": +0.15}, interests=("companionship",)),

    # ===== 2. SPORT / MOVEMENT =============================================
    ("2", "yes"): Scoring(deltas={"energy": +0.3, "intensity": +0.15}),
    ("2", "no"): Scoring(deltas={"energy": -0.15}),
    # 2a — how you prefer to move
    ("2a", "a"): Scoring(interests=("solo_training",)),
    ("2a", "b"): Scoring(deltas={"warmth": +0.05}, interests=("team_sport",)),
    ("2a", "c"): Scoring(deltas={"nature_affinity": +0.1}, interests=("outdoor_sport",)),
    ("2a", "d"): Scoring(deltas={"openness": +0.05}, interests=("free_movement",)),
    # 2b — what you seek in sport
    ("2b", "a"): Scoring(deltas={"energy": -0.05}, interests=("calm_focus",)),
    ("2b", "b"): Scoring(deltas={"intensity": +0.15}, interests=("ambition",)),
    ("2b", "c"): Scoring(deltas={"energy": +0.15, "intensity": +0.1}, interests=("adrenaline",)),
    ("2b", "d"): Scoring(interests=("embodiment",)),
    # 2c — how you feel after a good session
    ("2c", "a"): Scoring(deltas={"warmth": +0.05}, interests=("calm_focus",)),
    ("2c", "b"): Scoring(deltas={"energy": +0.15}, interests=("spark",)),
    ("2c", "c"): Scoring(deltas={"warmth": +0.05}, interests=("ambition",)),
    ("2c", "d"): Scoring(interests=("embodiment",)),

    # ===== 3. CHAOS vs ORDER ===============================================
    ("3", "yes"): Scoring(deltas={"openness": +0.3, "intensity": +0.15}),
    ("3", "no"): Scoring(deltas={"openness": -0.2}),
    # 3a — what kind of unpredictable attracts you
    ("3a", "a"): Scoring(deltas={"openness": +0.1}, interests=("wandering",)),
    ("3a", "b"): Scoring(deltas={"openness": +0.1}, interests=("discovery",)),
    ("3a", "c"): Scoring(deltas={"warmth": +0.05}, interests=("spontaneity",)),
    ("3a", "d"): Scoring(interests=("fluidity",)),
    # 3b — how you react in chaos
    ("3b", "a"): Scoring(deltas={"energy": +0.1, "intensity": +0.1}, interests=("energy_burst",)),
    ("3b", "b"): Scoring(deltas={"energy": -0.05}, interests=("detachment",)),
    ("3b", "c"): Scoring(deltas={"openness": +0.05}, interests=("ideas",)),
    ("3b", "d"): Scoring(interests=("surrender",)),
    # 3c — how you feel about routine
    ("3c", "a"): Scoring(deltas={"intensity": +0.1, "openness": +0.05}),
    ("3c", "b"): Scoring(deltas={"openness": +0.1}, interests=("spontaneity",)),
    ("3c", "c"): Scoring(deltas={"openness": -0.05}),
    ("3c", "d"): Scoring(),

    # ===== 4. EMOTION vs REASON ============================================
    ("4", "yes"): Scoring(deltas={"warmth": +0.2, "intensity": +0.2}),
    ("4", "no"): Scoring(deltas={"intensity": -0.1}),
    # 4a — which emotion defines you
    ("4a", "a"): Scoring(deltas={"warmth": +0.05}, interests=("nostalgia",)),
    ("4a", "b"): Scoring(interests=("longing",)),
    ("4a", "c"): Scoring(deltas={"energy": +0.1}, interests=("spark",)),
    ("4a", "d"): Scoring(interests=("melancholy",)),
    # 4b — how you process strong emotion
    ("4b", "a"): Scoring(deltas={"energy": +0.05}),
    ("4b", "b"): Scoring(deltas={"energy": -0.05}, interests=("introspection",)),
    ("4b", "c"): Scoring(deltas={"openness": +0.05}, interests=("creativity",)),
    ("4b", "d"): Scoring(deltas={"warmth": +0.1}, interests=("human_connection",)),
    # 4c — what moves you most
    ("4c", "a"): Scoring(interests=("music_notes",)),
    ("4c", "b"): Scoring(deltas={"warmth": +0.1}, interests=("human_connection",)),
    ("4c", "c"): Scoring(interests=("beauty",)),
    ("4c", "d"): Scoring(deltas={"openness": +0.1}, interests=("ideas",)),

    # ===== 5. MUSIC ========================================================
    ("5", "yes"): Scoring(deltas={"warmth": +0.15, "openness": +0.1}, interests=("music_notes",)),
    ("5", "no"): Scoring(),
    # 5a — what you feel when a song really lands
    ("5a", "a"): Scoring(deltas={"warmth": +0.05}, interests=("nostalgia",)),
    ("5a", "b"): Scoring(interests=("longing",)),
    ("5a", "c"): Scoring(deltas={"energy": +0.1}, interests=("dance",)),
    ("5a", "d"): Scoring(interests=("immersion",)),
    # 5b — when you most need music
    ("5b", "a"): Scoring(interests=("melancholy",)),
    ("5b", "b"): Scoring(deltas={"energy": +0.1}, interests=("spark",)),
    ("5b", "c"): Scoring(interests=("creativity",)),
    ("5b", "d"): Scoring(interests=("immersion",)),
    # 5c — your most-listened genre
    ("5c", "a"): Scoring(deltas={"warmth": +0.1, "energy": -0.05}, interests=("acoustic_warmth",)),
    ("5c", "b"): Scoring(deltas={"intensity": +0.15, "energy": +0.1}, interests=("electric_energy",)),
    ("5c", "c"): Scoring(deltas={"openness": +0.05}, interests=("varied_rhythm",)),
    ("5c", "d"): Scoring(interests=("varied_rhythm",)),
}
