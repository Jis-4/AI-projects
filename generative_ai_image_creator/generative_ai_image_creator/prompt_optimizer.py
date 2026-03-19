"""Prompt enhancement for marketing-focused creative generation."""

from __future__ import annotations

from dataclasses import dataclass
from typing import List


@dataclass
class PromptInput:
    brand: str
    product: str
    audience: str
    campaign_goal: str
    prompt: str
    style: str
    call_to_action: str
    use_case: str = "marketing"
    negative_prompt: str = ""


class PromptOptimizer:
    """Turns a rough idea into a provider-ready structured prompt."""

    QUALITY_TOKENS = [
        "high contrast composition",
        "clean hierarchy",
        "premium lighting",
        "brand-safe typography",
        "clear focal subject",
    ]

    USE_CASE_GUIDANCE = {
        "marketing": "design a polished campaign creative for paid social and landing page reuse",
        "avatar": "design a profile-ready avatar composition with strong silhouette and identity cues",
        "ui_mockup": "design a product mockup scene with clear interface framing and realistic device presentation",
    }

    def optimize(self, payload: PromptInput) -> dict:
        guidance = self.USE_CASE_GUIDANCE.get(payload.use_case, self.USE_CASE_GUIDANCE["marketing"])
        style_tokens = [token.strip() for token in payload.style.split(",") if token.strip()]
        constraints: List[str] = self.QUALITY_TOKENS + style_tokens
        optimized_prompt = (
            f"Brand: {payload.brand}. Product: {payload.product}. Audience: {payload.audience}. "
            f"Goal: {payload.campaign_goal}. Direction: {guidance}. Core concept: {payload.prompt}. "
            f"Include CTA '{payload.call_to_action}'. Visual style cues: {', '.join(constraints)}."
        )
        negative_prompt = payload.negative_prompt or (
            "avoid clutter, unreadable text, low-contrast elements, distorted objects, and off-brand colors"
        )
        return {
            "optimized_prompt": optimized_prompt,
            "negative_prompt": negative_prompt,
            "prompt_score": min(100, 60 + len(constraints) * 4 + (12 if payload.negative_prompt else 0)),
            "recommendations": [
                "Keep one dominant message and one CTA.",
                "Use a high-contrast focal area for the hero visual.",
                f"Tailor copy to the {payload.audience} audience segment.",
            ],
        }
