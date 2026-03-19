"""Core orchestration for generation, ranking, and editing."""

from __future__ import annotations

from pathlib import Path

from .creative_engine import LocalCreativeEngine
from .prompt_optimizer import PromptInput, PromptOptimizer
from .repository import CreativeRepository, to_dict


class CreativeStudioService:
    def __init__(self, repository: CreativeRepository, engine: LocalCreativeEngine, optimizer: PromptOptimizer) -> None:
        self.repository = repository
        self.engine = engine
        self.optimizer = optimizer

    def generate(self, payload: dict) -> dict:
        prompt_fields = {
            "brand": payload["brand"],
            "product": payload["product"],
            "audience": payload["audience"],
            "campaign_goal": payload["campaign_goal"],
            "prompt": payload["prompt"],
            "style": payload["style"],
            "call_to_action": payload["call_to_action"],
            "use_case": payload["use_case"],
            "negative_prompt": payload.get("negative_prompt", ""),
        }
        prompt_result = self.optimizer.optimize(PromptInput(**prompt_fields))
        variants = self.engine.create_variants(payload, prompt_result["optimized_prompt"], count=payload.get("variants", 4))
        created_ids = []
        for variant in variants:
            created_ids.append(
                self.repository.add_creative(
                    {
                        "project_name": payload["project_name"],
                        "use_case": payload["use_case"],
                        "brand": payload["brand"],
                        "product": payload["product"],
                        "headline": variant["headline"],
                        "optimized_prompt": prompt_result["optimized_prompt"],
                        "original_prompt": payload["prompt"],
                        "negative_prompt": prompt_result["negative_prompt"],
                        "style_preset": payload["style"],
                        "palette": variant["palette"],
                        "layout": variant["layout"],
                        "score": variant["score"],
                        "favorite": 0,
                        "rating": 0,
                        "asset_path": variant["asset_path"],
                        "edit_instruction": "",
                        "parent_id": None,
                    }
                )
            )
        created = [self.repository.get_creative(record_id).__dict__ for record_id in created_ids]
        return {
            "prompt": prompt_result,
            "created": created,
            "top_ranked": to_dict(self.repository.top_ranked()),
        }

    def list_creatives(self, use_case: str | None = None) -> dict:
        return {
            "items": to_dict(self.repository.list_creatives(use_case=use_case)),
            "top_ranked": to_dict(self.repository.top_ranked()),
        }

    def rate_creative(self, creative_id: int, rating: int, favorite: bool) -> dict:
        self.repository.update_feedback(creative_id, rating, favorite)
        record = self.repository.get_creative(creative_id)
        return {"item": record.__dict__, "top_ranked": to_dict(self.repository.top_ranked())}

    def edit_creative(self, creative_id: int, edit_payload: dict) -> dict:
        record = self.repository.get_creative(creative_id)
        if record is None:
            raise ValueError(f"Creative {creative_id} not found")
        output_name = Path(record.asset_path).stem + f"-edit-{creative_id}.svg"
        asset_path = self.engine.apply_edit(Path(record.asset_path), output_name, edit_payload, {**record.__dict__, "call_to_action": edit_payload.get("call_to_action", "Learn More")})
        new_id = self.repository.add_creative(
            {
                "project_name": record.project_name,
                "use_case": record.use_case,
                "brand": record.brand,
                "product": record.product,
                "headline": edit_payload.get("replacement_text") or record.headline,
                "optimized_prompt": record.optimized_prompt,
                "original_prompt": record.original_prompt,
                "negative_prompt": record.negative_prompt,
                "style_preset": edit_payload.get("style_preset") or record.style_preset,
                "palette": edit_payload.get("palette") or record.palette,
                "layout": edit_payload.get("layout") or record.layout,
                "score": max(record.score, 60),
                "favorite": 0,
                "rating": 0,
                "asset_path": asset_path,
                "edit_instruction": edit_payload.get("edit_instruction", ""),
                "parent_id": record.id,
            }
        )
        updated = self.repository.get_creative(new_id)
        return {"item": updated.__dict__, "top_ranked": to_dict(self.repository.top_ranked())}
