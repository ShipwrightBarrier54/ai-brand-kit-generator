"""Font registry — scans Windows font dirs and bundled fonts."""
from __future__ import annotations

import logging
import random
from dataclasses import dataclass
from pathlib import Path

log = logging.getLogger(__name__)

WINDOWS_FONT_DIRS = (
    Path(r"C:\Windows\Fonts"),
    Path.home() / "AppData" / "Local" / "Microsoft" / "Windows" / "Fonts",
)
BUNDLED_DIR = Path(__file__).resolve().parent.parent / "config" / "fonts"


@dataclass(slots=True)
class FontFace:
    family: str
    path: Path
    category: str  # sans | serif | mono | display


class FontRegistry:
    _default: "FontRegistry | None" = None

    def __init__(self, faces: list[FontFace]) -> None:
        self._faces = faces
        self._by_family = {f.family: f for f in faces}

    @classmethod
    def default(cls) -> "FontRegistry":
        if cls._default is None:
            cls._default = cls(cls._scan())
        return cls._default

    def families(self) -> list[str]:
        return sorted(self._by_family)

    def path_for(self, family: str) -> Path:
        face = self._by_family.get(family)
        if face is None:
            raise KeyError(f"font family not registered: {family}")
        return face.path

    def pick(self, category: str, rng: random.Random, exclude: set[str] | None = None) -> FontFace:
        exclude = exclude or set()
        pool = [f for f in self._faces if f.category == category and f.family not in exclude]
        if not pool:
            pool = [f for f in self._faces if f.family not in exclude] or self._faces
        return rng.choice(pool)

    @staticmethod
    def _scan() -> list[FontFace]:
        faces: list[FontFace] = []
        for d in (*WINDOWS_FONT_DIRS, BUNDLED_DIR):
            if not d.exists():
                continue
            for p in d.glob("*.ttf"):
                family = p.stem.split("-")[0]
                faces.append(FontFace(family=family, path=p, category=_guess_category(family)))
        if not faces:
            log.warning("no fonts found; typography generator will use fallbacks")
        return faces


def _guess_category(family: str) -> str:
    low = family.lower()
    if any(k in low for k in ("mono", "consol", "courier")):
        return "mono"
    if any(k in low for k in ("serif", "times", "georgia", "garamond")):
        return "serif"
    if any(k in low for k in ("display", "impact", "black")):
        return "display"
    return "sans"