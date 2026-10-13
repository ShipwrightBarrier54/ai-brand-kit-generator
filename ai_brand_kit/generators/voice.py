"""Voice & tone generator — produces brand voice guidelines.

Deterministic template composition driven by the brief's traits and the
preset's tone axes. The neural backend is optional and off by default.
"""
from __future__ import annotations

from typing import TYPE_CHECKING

from ai_brand_kit.generators.base import BaseGenerator, StageResult
from ai_brand_kit.models.kit import KitAsset

if TYPE_CHECKING:
    from ai_brand_kit.core.pipeline import PipelineContext

AXES = ("formal", "playful", "technical", "warm", "bold", "minimal")


class VoiceGenerator(BaseGenerator):
    name = "voice"
    priority = 40

    def generate(self, ctx: "PipelineContext") -> StageResult:
        traits = ctx.brief.traits or ["clear", "confident"]
        scores = {axis: round(ctx.rng.uniform(0.2, 0.9), 2) for axis in AXES}
        for t in traits:
            if t in scores:
                scores[t] = min(1.0, scores[t] + 0.2)

        dos = [f"Sound {t}." for t in traits[:3]]
        donts = [f"Don't oversell — the brand is {traits[0]}."]
        data = {
            "axes": scores,
            "do": dos,
            "dont": donts,
            "tagline_options": self._taglines(ctx),
        }
        asset = KitAsset(kind="voice", name=f"{ctx.brief.slug()}-voice", path=None, meta=data)
        return StageResult(stage=self.name, assets=[asset], data=data)

    def _taglines(self, ctx: "PipelineContext") -> list[str]:
        name = ctx.brief.name
        return [
            f"{name}. Built for the ones who ship.",
            f"{name} — clear by default.",
            f"Make it {name.lower()}.",
        ]