"""Palette generator — derives a color system from the brief.

Uses OKLCH for perceptual uniformity. Base hue is seeded from the brand
name hash so the same brief always yields the same palette family.
"""
from __future__ import annotations

import colorsys
import hashlib
from typing import TYPE_CHECKING

from ai_brand_kit.generators.base import BaseGenerator, StageResult
from ai_brand_kit.models.kit import KitAsset
from ai_brand_kit.utils.color import oklch_to_hex, shift_hue

if TYPE_CHECKING:
    from ai_brand_kit.core.pipeline import PipelineContext


class PaletteGenerator(BaseGenerator):
    name = "palette"
    priority = 10

    def generate(self, ctx: "PipelineContext") -> StageResult:
        brief = ctx.brief
        anchor = self._anchor_hue(brief.name)
        mood = ctx.preset.get("palette", {})
        base_l = float(mood.get("lightness", 0.62))
        base_c = float(mood.get("chroma", 0.14))
        harmony = mood.get("harmony", "analogous")

        hues = self._harmony_hues(anchor, harmony)
        palette: dict[str, str] = {}
        for i, h in enumerate(hues):
            l = base_l + (i - len(hues) / 2) * 0.05
            palette[f"accent_{i + 1}"] = oklch_to_hex(l, base_c, h)
        palette["ink"] = oklch_to_hex(0.18, 0.02, anchor)
        palette["paper"] = oklch_to_hex(0.97, 0.01, anchor)

        asset = KitAsset(
            kind="palette",
            name=f"{brief.slug()}-palette",
            path=None,
            meta={"harmony": harmony, "colors": palette},
        )
        return StageResult(stage=self.name, assets=[asset], data=palette)

    @staticmethod
    def _anchor_hue(name: str) -> float:
        digest = hashlib.sha256(name.encode("utf-8")).digest()
        return (int.from_bytes(digest[:4], "big") / 2**32) * 360.0

    @staticmethod
    def _harmony_hues(anchor: float, harmony: str) -> list[float]:
        if harmony == "complementary":
            return [anchor, shift_hue(anchor, 180)]
        if harmony == "triadic":
            return [anchor, shift_hue(anchor, 120), shift_hue(anchor, 240)]
        if harmony == "split":
            return [anchor, shift_hue(anchor, 150), shift_hue(anchor, 210)]
        # default: analogous
        return [shift_hue(anchor, d) for d in (-30, -15, 0, 15, 30)]