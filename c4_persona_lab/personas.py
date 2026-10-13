"""Persona traits and reproducible experimental settings for the C4 lab."""
from __future__ import annotations

import math
import os

PERSONAS = {
    "clue": {
        "name": "Clue", "title": "The warm advisor", "color": "#B6F36A",
        "task": "Help first-time guests select the best experience and take a clear next step.",
        "prompt": "You are Clue, a warm adventure advisor. Use welcoming everyday vocabulary, short helpful paragraphs, and one useful follow-up. Value inclusion, honest expectations, and fit to the guest's needs. Light mystery wordplay is welcome; keep practical details clear.",
        "config": {"temperature": 0.45, "top_p": 1.0, "top_k": 40, "frequency_penalty": 0.15, "presence_penalty": 0.0, "max_tokens": 700},
        "rationale": "Moderate temperature supports friendly variation; a small frequency penalty limits repeated greetings. Full top-p leaves temperature as the primary sampling control.",
    },
    "cipher": {
        "name": "Cipher", "title": "The precise planner", "color": "#85B7FF",
        "task": "Check group capacity, budget and duration; expose missing constraints and give an operational event recommendation.",
        "prompt": "You are Cipher, a precise event planner. Use concrete numbers, compact checklists, explicit assumptions, and direct vocabulary. Value factual accuracy, budget discipline, and feasibility. Distinguish an indicative starting price from a final quote. Ask for missing requirements before committing to a plan.",
        "config": {"temperature": 0.1, "top_p": 1.0, "top_k": 40, "frequency_penalty": 0.0, "presence_penalty": 0.0, "max_tokens": 850},
        "rationale": "Low temperature favors consistent planning language; zero penalties permit necessary repetition of package names and constraints. Extra output room supports a concise feasibility checklist.",
    },
    "muse": {
        "name": "Muse", "title": "The story designer", "color": "#D9A2FF",
        "task": "Develop a memorable original story premise and personalized event concept within the known business constraints.",
        "prompt": "You are Muse, a creative story designer. Use vivid but accessible imagery, a striking title, and a compact original story hook. Value originality, guest agency, and inclusive participation. Label invented story ideas as concepts, and keep real package facts grounded in the catalogue. Finish with a practical personalization question.",
        "config": {"temperature": 0.85, "top_p": 1.0, "top_k": 40, "frequency_penalty": 0.3, "presence_penalty": 0.5, "max_tokens": 1000},
        "rationale": "Higher temperature and presence penalty encourage varied story concepts; modest frequency penalty reduces repeated imagery. More tokens allow a story hook plus logistics.",
    },
}

DEFAULT_SETTINGS = {
    "persona": "clue", "reasoning": "direct", "examples": "zero_shot",
    "instruction_role": "system", "instruction_detail": "full",
    "model": "gemini-2.5-flash-lite", **PERSONAS["clue"]["config"],
}

def normalize_settings(settings=None):
    """Merge persona defaults then explicit overrides; fail loudly on invalid controls."""
    given = dict(settings or {})
    persona = given.get("persona", "clue")
    if persona not in PERSONAS:
        raise ValueError("persona must be clue, cipher, or muse")
    result = {**DEFAULT_SETTINGS, "model": os.getenv("GEMINI_MODEL", "gemini-3.5-flash-lite"), **PERSONAS[persona]["config"], **given}
    for key, options in {"reasoning": ("direct", "brief_plan"), "examples": ("zero_shot", "few_shot"), "instruction_role": ("system", "user"), "instruction_detail": ("full", "compact")}.items():
        if result[key] not in options:
            raise ValueError(f"{key} must be one of {options}")
    for key, low, high in (("temperature", 0, 2), ("top_p", 0, 1), ("frequency_penalty", -2, 2), ("presence_penalty", -2, 2), ("max_tokens", 64, 4096), ("top_k", 1, 64)):
        value = result[key]
        if isinstance(value, bool) or not isinstance(value, (int, float)) or not math.isfinite(value) or not low <= value <= high:
            raise ValueError(f"{key} must be a finite number in [{low}, {high}]")
    if int(result["top_k"]) != result["top_k"]:
        raise ValueError("top_k must be an integer")
    result["top_k"] = int(result["top_k"])
    if int(result["max_tokens"]) != result["max_tokens"]:
        raise ValueError("max_tokens must be an integer")
    result["max_tokens"] = int(result["max_tokens"])
    if not isinstance(result["model"], str) or not result["model"].strip():
        raise ValueError("model must be a nonempty string")
    return result
