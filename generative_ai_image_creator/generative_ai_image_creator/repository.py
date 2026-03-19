"""SQLite persistence for generated creatives and rankings."""

from __future__ import annotations

import sqlite3
from pathlib import Path
from typing import Iterable, List, Optional

from .models import CreativeRecord


class CreativeRepository:
    def __init__(self, db_path: Path) -> None:
        self.db_path = db_path
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._initialize()

    def _connect(self) -> sqlite3.Connection:
        connection = sqlite3.connect(self.db_path)
        connection.row_factory = sqlite3.Row
        return connection

    def _initialize(self) -> None:
        with self._connect() as connection:
            connection.execute(
                """
                CREATE TABLE IF NOT EXISTS creatives (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    project_name TEXT NOT NULL,
                    use_case TEXT NOT NULL,
                    brand TEXT NOT NULL,
                    product TEXT NOT NULL,
                    headline TEXT NOT NULL,
                    optimized_prompt TEXT NOT NULL,
                    original_prompt TEXT NOT NULL,
                    negative_prompt TEXT NOT NULL,
                    style_preset TEXT NOT NULL,
                    palette TEXT NOT NULL,
                    layout TEXT NOT NULL,
                    score REAL NOT NULL DEFAULT 0,
                    favorite INTEGER NOT NULL DEFAULT 0,
                    rating INTEGER NOT NULL DEFAULT 0,
                    asset_path TEXT NOT NULL,
                    edit_instruction TEXT NOT NULL DEFAULT '',
                    parent_id INTEGER,
                    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
                )
                """
            )

    def add_creative(self, payload: dict) -> int:
        fields = [
            "project_name",
            "use_case",
            "brand",
            "product",
            "headline",
            "optimized_prompt",
            "original_prompt",
            "negative_prompt",
            "style_preset",
            "palette",
            "layout",
            "score",
            "favorite",
            "rating",
            "asset_path",
            "edit_instruction",
            "parent_id",
        ]
        values = [payload.get(field) for field in fields]
        placeholders = ", ".join("?" for _ in fields)
        with self._connect() as connection:
            cursor = connection.execute(
                f"INSERT INTO creatives ({', '.join(fields)}) VALUES ({placeholders})",
                values,
            )
            return int(cursor.lastrowid)

    def list_creatives(self, use_case: Optional[str] = None) -> List[CreativeRecord]:
        query = "SELECT * FROM creatives"
        params: list[object] = []
        if use_case:
            query += " WHERE use_case = ?"
            params.append(use_case)
        query += " ORDER BY score DESC, favorite DESC, created_at DESC"
        with self._connect() as connection:
            rows = connection.execute(query, params).fetchall()
        return [self._row_to_model(row) for row in rows]

    def get_creative(self, creative_id: int) -> CreativeRecord | None:
        with self._connect() as connection:
            row = connection.execute("SELECT * FROM creatives WHERE id = ?", [creative_id]).fetchone()
        return self._row_to_model(row) if row else None

    def update_feedback(self, creative_id: int, rating: int, favorite: bool) -> None:
        score = rating * 20 + (15 if favorite else 0)
        with self._connect() as connection:
            connection.execute(
                "UPDATE creatives SET rating = ?, favorite = ?, score = ? WHERE id = ?",
                [rating, int(favorite), score, creative_id],
            )

    def top_ranked(self, limit: int = 5) -> List[CreativeRecord]:
        with self._connect() as connection:
            rows = connection.execute(
                "SELECT * FROM creatives ORDER BY score DESC, favorite DESC, created_at DESC LIMIT ?",
                [limit],
            ).fetchall()
        return [self._row_to_model(row) for row in rows]

    def _row_to_model(self, row: sqlite3.Row) -> CreativeRecord:
        return CreativeRecord(
            id=row["id"],
            project_name=row["project_name"],
            use_case=row["use_case"],
            brand=row["brand"],
            product=row["product"],
            headline=row["headline"],
            optimized_prompt=row["optimized_prompt"],
            original_prompt=row["original_prompt"],
            negative_prompt=row["negative_prompt"],
            style_preset=row["style_preset"],
            palette=row["palette"],
            layout=row["layout"],
            score=row["score"],
            favorite=bool(row["favorite"]),
            rating=row["rating"],
            asset_path=row["asset_path"],
            edit_instruction=row["edit_instruction"],
            parent_id=row["parent_id"],
            created_at=row["created_at"],
        )


def to_dict(records: Iterable[CreativeRecord]) -> list[dict]:
    return [record.__dict__.copy() for record in records]
