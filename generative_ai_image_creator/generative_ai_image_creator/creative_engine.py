"""Local demo renderer for polished marketing creative mockups."""

from __future__ import annotations

import html
import random
from pathlib import Path


class LocalCreativeEngine:
    PALETTES = {
        "electric": ("#0B1026", "#6EE7F9", "#F9A826", "#FFFFFF"),
        "luxury": ("#1C1917", "#D4AF37", "#F5EFE6", "#FAFAF9"),
        "playful": ("#1D4ED8", "#F472B6", "#FDE047", "#FFFFFF"),
        "minimal": ("#0F172A", "#E2E8F0", "#38BDF8", "#FFFFFF"),
    }
    LAYOUTS = ["hero-left", "hero-right", "stacked", "spotlight"]

    def __init__(self, generated_dir: Path, seed: int = 42) -> None:
        self.generated_dir = generated_dir
        self.generated_dir.mkdir(parents=True, exist_ok=True)
        self.rng = random.Random(seed)

    def create_variants(self, payload: dict, optimized_prompt: str, count: int = 4) -> list[dict]:
        variants = []
        palette_names = list(self.PALETTES)
        for index in range(count):
            palette_name = palette_names[index % len(palette_names)]
            layout = self.LAYOUTS[index % len(self.LAYOUTS)]
            headline = self._headline(payload["brand"], payload["product"], payload["campaign_goal"], index)
            filename = self._slug(payload["project_name"]) + f"-{index + 1}.svg"
            asset_path = self.generated_dir / filename
            svg = self._render_svg(
                headline=headline,
                subhead=payload["prompt"],
                brand=payload["brand"],
                cta=payload["call_to_action"],
                use_case=payload["use_case"],
                palette_name=palette_name,
                layout=layout,
                style=payload["style"],
                optimized_prompt=optimized_prompt,
            )
            asset_path.write_text(svg, encoding="utf-8")
            variants.append(
                {
                    "headline": headline,
                    "palette": palette_name,
                    "layout": layout,
                    "asset_path": str(asset_path),
                    "score": self._initial_score(payload["style"], optimized_prompt, index),
                }
            )
        return variants

    def apply_edit(self, source_path: Path, output_name: str, edit_payload: dict, record: dict) -> str:
        palette_name = edit_payload.get("palette") or record["palette"]
        layout = edit_payload.get("layout") or record["layout"]
        headline = edit_payload.get("replacement_text") or record["headline"]
        subhead = edit_payload.get("edit_instruction") or record["original_prompt"]
        svg = self._render_svg(
            headline=headline,
            subhead=subhead,
            brand=record["brand"],
            cta=record.get("call_to_action", "Learn More"),
            use_case=record["use_case"],
            palette_name=palette_name,
            layout=layout,
            style=f"{record['style_preset']}, edit intensity {edit_payload.get('style_strength', 70)}",
            optimized_prompt=record["optimized_prompt"],
            mask_region=edit_payload.get("mask_region", "hero"),
        )
        destination = self.generated_dir / output_name
        destination.write_text(svg, encoding="utf-8")
        return str(destination)

    def _headline(self, brand: str, product: str, campaign_goal: str, index: int) -> str:
        templates = [
            f"{brand} makes {product} feel premium",
            f"Launch {product} with scroll-stopping impact",
            f"Turn {campaign_goal.lower()} into a branded visual story",
            f"{product}: the creative your audience remembers",
        ]
        return templates[index % len(templates)]

    def _initial_score(self, style: str, optimized_prompt: str, index: int) -> float:
        style_bonus = 8 if "cinematic" in style.lower() else 4
        return round(55 + style_bonus + min(18, len(optimized_prompt) / 25) - index * 2, 2)

    def _render_svg(
        self,
        *,
        headline: str,
        subhead: str,
        brand: str,
        cta: str,
        use_case: str,
        palette_name: str,
        layout: str,
        style: str,
        optimized_prompt: str,
        mask_region: str | None = None,
    ) -> str:
        background, accent, highlight, text = self.PALETTES.get(palette_name, self.PALETTES["electric"])
        hero_x = {"hero-left": 70, "hero-right": 700, "stacked": 390, "spotlight": 390}[layout]
        text_x = 520 if layout == "hero-left" else 80
        if layout == "stacked":
            text_x = 80
        hero_anchor = "middle" if layout in {"stacked", "spotlight"} else "middle"
        hero_size = 250 if layout != "spotlight" else 280
        escaped_headline = html.escape(headline)
        escaped_subhead = html.escape(subhead[:90])
        escaped_brand = html.escape(brand)
        escaped_cta = html.escape(cta)
        escaped_style = html.escape(style[:60])
        escaped_prompt = html.escape(optimized_prompt[:120])
        edit_overlay = ""
        if mask_region:
            overlay_positions = {
                "headline": (520, 150, 320, 90),
                "hero": (hero_x - hero_size / 2, 180, hero_size, hero_size),
                "cta": (text_x, 430, 180, 60),
                "background": (20, 20, 1160, 590),
            }
            x, y, width, height = overlay_positions.get(mask_region, overlay_positions["hero"])
            edit_overlay = (
                f'<rect x="{x}" y="{y}" width="{width}" height="{height}" '
                f'fill="none" stroke="{highlight}" stroke-width="4" stroke-dasharray="12 10" rx="18" />'
            )
        return f'''<svg width="1200" height="630" viewBox="0 0 1200 630" fill="none" xmlns="http://www.w3.org/2000/svg">
<defs>
  <linearGradient id="bg" x1="0" y1="0" x2="1200" y2="630" gradientUnits="userSpaceOnUse">
    <stop stop-color="{background}" />
    <stop offset="1" stop-color="{accent}" />
  </linearGradient>
</defs>
<rect width="1200" height="630" rx="36" fill="url(#bg)" />
<circle cx="{hero_x}" cy="315" r="{hero_size}" fill="{highlight}" fill-opacity="0.18" />
<circle cx="{hero_x}" cy="315" r="{hero_size - 40}" fill="{background}" fill-opacity="0.45" stroke="{highlight}" stroke-width="2" />
<rect x="60" y="48" width="180" height="44" rx="22" fill="{highlight}" fill-opacity="0.18" />
<text x="90" y="77" fill="{text}" font-size="24" font-family="Arial, Helvetica, sans-serif" font-weight="700">{escaped_brand}</text>
<text x="{text_x}" y="180" fill="{text}" font-size="54" font-family="Arial, Helvetica, sans-serif" font-weight="700">{escaped_headline}</text>
<text x="{text_x}" y="240" fill="{text}" font-size="24" font-family="Arial, Helvetica, sans-serif" opacity="0.86">{escaped_subhead}</text>
<text x="{text_x}" y="285" fill="{text}" font-size="18" font-family="Arial, Helvetica, sans-serif" opacity="0.68">Use case: {html.escape(use_case.replace('_', ' '))}</text>
<rect x="{text_x}" y="410" width="190" height="58" rx="29" fill="{highlight}" />
<text x="{text_x + 95}" y="447" fill="{background}" text-anchor="middle" font-size="22" font-family="Arial, Helvetica, sans-serif" font-weight="700">{escaped_cta}</text>
<rect x="{text_x}" y="500" width="420" height="82" rx="20" fill="#FFFFFF" fill-opacity="0.08" />
<text x="{text_x + 24}" y="530" fill="{text}" font-size="16" font-family="Arial, Helvetica, sans-serif" opacity="0.78">Style: {escaped_style}</text>
<text x="{text_x + 24}" y="558" fill="{text}" font-size="14" font-family="Arial, Helvetica, sans-serif" opacity="0.68">Prompt: {escaped_prompt}</text>
<g transform="translate({hero_x - 90},225)">
  <rect width="180" height="180" rx="32" fill="{highlight}" fill-opacity="0.26" />
  <path d="M30 126C58 46 118 20 150 32C120 62 124 112 154 148C102 166 56 160 30 126Z" fill="{highlight}" />
  <circle cx="116" cy="70" r="28" fill="{text}" fill-opacity="0.18" />
  <text x="90" y="170" text-anchor="middle" fill="{text}" font-size="24" font-family="Arial, Helvetica, sans-serif" font-weight="700">{hero_anchor}</text>
</g>
{edit_overlay}
</svg>'''

    def _slug(self, value: str) -> str:
        return "-".join(part.lower() for part in value.split() if part).strip("-") or "creative"
