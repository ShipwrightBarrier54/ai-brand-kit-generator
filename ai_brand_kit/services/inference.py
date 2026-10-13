"""Optional neural backend for logo/voice generation.

Off by default. Enable with preset.logo.backend = "neural". Talks to a
local ONNX Runtime session or a user-configured HTTP endpoint. Never
sends the brief anywhere unless inference_endpoint is explicitly set.
"""
from __future__ import annotations

import logging
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import httpx

log = logging.getLogger(__name__)


@dataclass(slots=True)
class InferenceConfig:
    backend: str = "geometric"  # geometric | onnx | http
    model_path: Path | None = None
    inference_endpoint: str | None = None
    timeout_s: float = 30.0


class InferenceClient:
    def __init__(self, cfg: InferenceConfig) -> None:
        self.cfg = cfg

    def available(self) -> bool:
        if self.cfg.backend == "onnx":
            return self.cfg.model_path is not None and self.cfg.model_path.exists()
        if self.cfg.backend == "http":
            return bool(self.cfg.inference_endpoint)
        return False

    def generate_logo(self, prompt: str, size: int = 1024) -> bytes:
        if self.cfg.backend == "http":
            return self._http_logo(prompt