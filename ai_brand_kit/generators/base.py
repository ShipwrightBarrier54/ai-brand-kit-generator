"""Base generator contract.

A generator takes a PipelineContext and returns a StageResult. Generators
must be side-effect free except for writing into ctx.out_dir when the
stage owns an artifact file (e.g. logo PNGs). Determinism comes from
ctx.rng — never call random directly.
"""
from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Any

from ai_brand_kit.models.kit import KitAsset

if TYPE_CHECKING:
    from ai_brand_kit.core.pipeline import PipelineContext


@dataclass(slots=True)
class StageResult:
    stage: str
    assets: list[KitAsset] = field(default_factory=list)
    data: dict[str, Any] = field(default_factory=dict)


class BaseGenerator(ABC):
    """Subclass this and register in registry.build_default_registry()."""

    name: str = "unnamed"
    priority: int = 100

    @abstractmethod
    def generate(self, ctx: "PipelineContext") -> StageResult:
        """Run the stage and return produced assets + stage data."""
        raise NotImplementedError