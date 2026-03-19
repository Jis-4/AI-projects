import tempfile
import unittest
from pathlib import Path

from generative_ai_image_creator.creative_engine import LocalCreativeEngine
from generative_ai_image_creator.prompt_optimizer import PromptInput, PromptOptimizer
from generative_ai_image_creator.repository import CreativeRepository
from generative_ai_image_creator.service import CreativeStudioService


class MarketingCreativeStudioTests(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        base_path = Path(self.temp_dir.name)
        self.repository = CreativeRepository(base_path / "studio.db")
        self.engine = LocalCreativeEngine(base_path / "generated")
        self.optimizer = PromptOptimizer()
        self.service = CreativeStudioService(self.repository, self.engine, self.optimizer)
        self.payload = {
            "project_name": "Launch Sprint",
            "use_case": "marketing",
            "brand": "Nova Labs",
            "product": "Glow Serum",
            "audience": "skincare shoppers",
            "campaign_goal": "Increase conversions",
            "prompt": "Make a luxury skincare ad with a clear CTA",
            "style": "cinematic, premium, glossy",
            "call_to_action": "Shop Now",
            "negative_prompt": "avoid clutter",
            "variants": 3,
        }

    def tearDown(self):
        self.temp_dir.cleanup()

    def test_prompt_optimizer_adds_structure(self):
        result = self.optimizer.optimize(PromptInput(
            brand=self.payload["brand"],
            product=self.payload["product"],
            audience=self.payload["audience"],
            campaign_goal=self.payload["campaign_goal"],
            prompt=self.payload["prompt"],
            style=self.payload["style"],
            call_to_action=self.payload["call_to_action"],
            use_case=self.payload["use_case"],
            negative_prompt=self.payload["negative_prompt"],
        ))
        self.assertIn("Brand: Nova Labs", result["optimized_prompt"])
        self.assertGreaterEqual(result["prompt_score"], 60)
        self.assertEqual(len(result["recommendations"]), 3)

    def test_generate_stores_ranked_creatives(self):
        result = self.service.generate(self.payload)
        self.assertEqual(len(result["created"]), 3)
        stored = self.repository.list_creatives(use_case="marketing")
        self.assertEqual(len(stored), 3)
        self.assertTrue(all(Path(item.asset_path).exists() for item in stored))
        self.assertTrue(result["top_ranked"][0]["score"] >= result["top_ranked"][-1]["score"])

    def test_rating_and_editing_create_new_version(self):
        created = self.service.generate(self.payload)["created"]
        creative_id = created[0]["id"]
        rated = self.service.rate_creative(creative_id, rating=5, favorite=True)
        self.assertEqual(rated["item"]["rating"], 5)
        self.assertTrue(rated["item"]["favorite"])

        edited = self.service.edit_creative(
            creative_id,
            {
                "mask_region": "headline",
                "replacement_text": "Glow that stops the scroll",
                "edit_instruction": "Make the headline more direct and premium.",
                "palette": "luxury",
                "layout": "hero-right",
                "style_strength": 88,
            },
        )
        self.assertEqual(edited["item"]["parent_id"], creative_id)
        self.assertTrue(Path(edited["item"]["asset_path"]).exists())
        self.assertEqual(len(self.repository.list_creatives(use_case="marketing")), 4)


if __name__ == "__main__":
    unittest.main()
