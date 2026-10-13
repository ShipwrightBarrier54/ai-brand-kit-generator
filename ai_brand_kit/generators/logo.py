"""Logo generator — produces raster logo concepts as PNGs.

This is a deterministic geometric generator, not a diffusion model. The
optional neural backend lives in services/inference.py and is used only
when preset.logo.backend == "neural".
"""
from __future__ import annotations

import logging
from pathlib import Path
from typing import TYPE_CHECKING

from PIL import Image, ImageDraw, ImageFont

from ai_brand_kit.generators.base import BaseGenerator, StageResult
from ai_brand_kit.models.kit import KitAsset
from ai_brand_kit.services.fonts import FontRegistry
from ai_brand_kit.utils.color import hex_to_rgb

if TYPE_CHECKING:
    from ai_brand_kit.core.pipeline import PipelineContext

log = logging.getLogger(__name__)


class LogoGenerator(BaseGenerator):
    name = "logo"
    priority = 30

    def generate(self, ctx: "PipelineContext") -> StageResult:
        palette = ctx.artifacts.get("palette", {})
        ink = hex_to_rgb(palette.get("ink", "#111111"))
        accent = hex_to_rgb(palette.get("accent_1", "#3366cc"))
        size = int(ctx.preset.get("logo", {}).get("size", 1024))
        count = int(ctx.preset.get("logo", {}).get("concepts", 3))

        out_dir = ctx.out_dir / "logo"
        out_dir.mkdir(parents=True, exist_ok=True)

        assets: list[KitAsset] = []
        for i in range(count):
            img = Image.new("RGBA", (size, size), (255, 255, 255, 0))
            draw = ImageDraw.Draw(img)
            self._draw_mark(draw, size, accent, i, ctx)
            self._draw_wordmark(draw, size, ink, ctx)
            path = out_dir / f"concept_{i + 1:02d}.png"
            img.save(path, "PNG")
            assets.append(
                KitAsset(kind="logo", name=f"concept_{i + 1:02d}", path=path, meta={"size": size})
            )
            log.debug("logo concept written %s", path)
        return StageResult(stage=self.name, assets=assets, data={"count": count})

    def _draw_mark(self, draw: ImageDraw.ImageDraw, size: int, color: tuple[int, int, int], idx: int, ctx: "PipelineContext") -> None:
        cx, cy = size // 2, int(size * 0.42)
        r = int(size * 0.18)
        if idx % 3 == 0:
            draw.ellipse((cx - r, cy - r, cx + r, cy + r), fill=color)
        elif idx % 3 == 1:
            draw.regular_polygon((cx, cy, r), n_sides=6, fill=color)
        else:
            draw.rounded_rectangle((cx - r, cy - r, cx + r, cy + r), radius=r // 3, fill=color)

    def _draw_wordmark(self, draw: ImageDraw.ImageDraw, size: int, color: tuple[int, int, int], ctx: "PipelineContext") -> None:
        name = ctx.brief.name.upper()
        try:
            font_path = FontRegistry.default().path_for(ctx.artifacts.get("typography", {}).get("headings", "Inter"))
            font = ImageFont.truetype(str(font_path), size=int(size * 0.09))
        except Exception:  # noqa: BLE001 - fall back to default bitmap font
            font = ImageFont.load_default()
        bbox = draw.textbbox((0, 0), name, font=font)
        w = bbox[2] - bbox[0]
        draw.text(((size - w) // 2, int(size * 0.68)), name, fill=color, font=font)