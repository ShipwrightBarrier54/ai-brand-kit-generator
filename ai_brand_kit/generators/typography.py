"""Typography generator — picks a heading/body pairing from the font registry."""
from __future__ import annotations

from typing import TYPE_CHECKING

from ai_brand_kit.generators.base import BaseGenerator, StageResult
from ai_brand_kit.models.kit import KitAsset
from ai_brand_kit.services.fonts import FontRegistry

if TYPE_CHECKING:
    from ai_brand_kit.core.pipeline import PipelineContext


class TypographyGenerator(BaseGenerator):
    name = "typography"
    priority = 20

    def generate(self, ctx: "PipelineContext") -> StageResult:
        registry = FontRegistry.default()
        mood = ctx.preset.get("typography", {})
        want_serif = bool(mood.get("serif_headings", False))

        headings = registry.pick(category="serif" if want_serif else "sans", rng=ctx.rng)
        body = registry.pick(category="sans", rng=ctx.rng, exclude={headings.family})
        mono = registry.pick(category="mono", rng=ctx.rng)

        scale = mood.get("scale", [12, 14, 16, 20, 24, 32, 48, 64])
        data = {
            "headings": headings.family,
            "body": body.family,
            "mono": mono.family,
            "scale_px": scale,
            "line_height": float(mood.get("line_height", 1.5)),
            "tracking_em": float(mood.get("tracking", 0.0)),
        }
        asset = KitAsset(kind="typography", name=f"{ctx.brief.slug()}-type", path=None, meta=data)
        return StageResult(stage=self.name, assets=[asset], data=data)