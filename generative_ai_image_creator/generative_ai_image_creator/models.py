"""Data models used by the creative studio service."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Optional


@dataclass
class CreativeRecord:
    id: int
    project_name: str
    use_case: str
    brand: str
    product: str
    headline: str
    optimized_prompt: str
    original_prompt: str
    negative_prompt: str
    style_preset: str
    palette: str
    layout: str
    score: float
    favorite: bool
    rating: int
    asset_path: str
    edit_instruction: str
    parent_id: Optional[int]
    created_at: str
