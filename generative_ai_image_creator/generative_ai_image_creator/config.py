"""Application configuration helpers."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class AppConfig:
    base_dir: Path
    db_path: Path
    generated_dir: Path
    static_dir: Path
    host: str = "127.0.0.1"
    port: int = 8000

    @classmethod
    def default(cls) -> "AppConfig":
        project_root = Path(__file__).resolve().parent.parent
        return cls(
            base_dir=project_root,
            db_path=project_root / "data" / "creative_studio.db",
            generated_dir=project_root / "data" / "generated",
            static_dir=project_root / "generative_ai_image_creator" / "static",
        )
