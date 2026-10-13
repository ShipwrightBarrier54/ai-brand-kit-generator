"""Brand kit pipeline — orchestrates generators in dependency order.

The pipeline is a small DAG: brief -> palette -> typography -> logo ->
voice -> exporter. Each stage consumes the previous stage's output and
emits a typed artifact. Stages are registered by name and can be
overridden by plugins.
"""
from __future__ import annotations

import logging
import random
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from ai_brand_kit.config.presets import load_preset
from ai_brand_kit.generators.registry import build_default_registry
from ai_brand_kit.models.brief import BrandBrief
from ai_brand_kit.models.kit import BrandKit, KitAsset
from ai_brand_kit.services.exporter import Exporter

log = logging.getLogger(__name__)


@dataclass(slots=True)
class PipelineContext:
    brief: BrandBrief
    preset: dict[str, Any]
    rng: random.Random
    out_dir: Path
    artifacts: dict[str, Any] = field(default_factory=dict)
    warnings: list[str] = field(default_factory=list)


class BrandKitPipeline:
    """Ordered generator pipeline. Deterministic given the same seed."""

    STAGE_ORDER = ("palette", "typography", "logo", "voice")

    def __init__(self, preset: str = "default", seed: int | None = None) -> None:
        self.preset_name = preset
        self.seed = seed if seed is not None else random.SystemRandom().randint(0, 2**31 - 1)
        self._registry = build_default_registry()

    def run(self, brief: BrandBrief, out_dir: Path) -> BrandKit:
        out_dir = Path(out_dir)
        out_dir.mkdir(parents=True, exist_ok=True)
        ctx = PipelineContext(
            brief=brief,
            preset=load_preset(self.preset_name),
            rng=random.Random(self.seed),
            out_dir=out_dir,
        )
        log.info("pipeline start preset=%s seed=%d", self.preset_name, self.seed)

        assets: list[KitAsset] = []
        for stage in self.STAGE_ORDER:
            gen = self._registry.get(stage)
            if gen is None:
                ctx.warnings.append(f"stage missing: {stage}")
                continue
            log.debug("running stage=%s", stage)
            produced = gen.generate(ctx)
            ctx.artifacts[stage] = produced
            assets.extend(produced.assets)

        exporter = Exporter(out_dir=out_dir, preset=ctx.preset)
        bundle = exporter.bundle(brief, assets, ctx.artifacts)

        kit = BrandKit(
            name=brief.name,
            slug=brief.slug(),
            seed=self.seed,
            preset=self.preset_name,
            root=bundle.root,
            assets=assets,
            warnings=ctx.warnings,
        )
        log.info("pipeline done assets=%d warnings=%d", len(assets), len(ctx.warnings))
        return kit