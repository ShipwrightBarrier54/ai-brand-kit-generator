"""Generator registry — resolves stage names to generator instances."""
from __future__ import annotations

from ai_brand_kit.generators.base import BaseGenerator
from ai_brand_kit.generators.logo import LogoGenerator
from ai_brand_kit.generators.palette import PaletteGenerator
from ai_brand_kit.generators.typography import TypographyGenerator
from ai_brand_kit.generators.voice import VoiceGenerator


class GeneratorRegistry:
    def __init__(self) -> None:
        self._by_name: dict[str, BaseGenerator] = {}

    def register(self, gen: BaseGenerator) -> None:
        self._by_name[gen.name] = gen

    def get(self, name: str) -> BaseGenerator | None:
        return self._by_name.get(name)

    def names(self) -> list[str]:
        return sorted(self._by_name)


def build_default_registry() -> GeneratorRegistry:
    reg = GeneratorRegistry()
    for gen in (PaletteGenerator(), TypographyGenerator(), LogoGenerator(), VoiceGenerator()):
        reg.register(gen)
    return reg