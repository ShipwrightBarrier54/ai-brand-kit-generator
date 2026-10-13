"""Plugin loader for third-party generators.

Plugins live under %APPDATA%\\ai-brand-kit-generator\\plugins by default.
Each plugin is a directory with a manifest.toml and a module exposing a
`register(registry)` function. Only plugins from trusted directories are
loaded — see SECURITY.md.
"""
from __future__ import annotations

import importlib.util
import logging
import tomllib
from dataclasses import dataclass
from pathlib import Path

from platformdirs import user_data_dir

log = logging.getLogger(__name__)


@dataclass(slots=True)
class PluginInfo:
    name: str
    version: str
    path: Path
    enabled: bool


class PluginLoader:
    DEFAULT_DIR = Path(user_data_dir("ai-brand-kit-generator")) / "plugins"

    def __init__(self, plugin_dir: Path | None = None) -> None:
        self.plugin_dir = plugin_dir or self.DEFAULT_DIR
        self._disabled_file = self.plugin_dir / ".disabled"

    def discover(self) -> list[PluginInfo]:
        if not self.plugin_dir.exists():
            return []
        disabled = self._read_disabled()
        out: list[PluginInfo] = []
        for entry in sorted(self.plugin_dir.iterdir()):
            manifest = entry / "manifest.toml"
            if not entry.is_dir() or not manifest.exists():
                continue
            try:
                data = tomllib.loads(manifest.read_text(encoding="utf-8"))
            except tomllib.TOMLDecodeError as exc:
                log.warning("bad manifest %s: %s", manifest, exc)
                continue
            out.append(
                PluginInfo(
                    name=data.get("name", entry.name),
                    version=data.get("version", "0.0.0"),
                    path=entry,
                    enabled=entry.name not in disabled,
                )
            )
        return out

    def set_enabled(self, name: str, enabled: bool) -> None:
        disabled = self._read_disabled()
        if enabled:
            disabled.discard(name)
        else:
            disabled.add(name)
        self.plugin_dir.mkdir(parents=True, exist_ok=True)
        self._disabled_file.write_text("\n".join(sorted(disabled)), encoding="utf-8")

    def load_module(self, info: PluginInfo) -> object:
        module_file = info.path / "plugin.py"
        spec = importlib.util.spec_from_file_location(f"brandkit_plugin_{info.name}", module_file)
        if spec is None or spec.loader is None:
            raise ImportError(f"cannot load plugin {info.name} from {module_file}")
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        return module

    def _read_disabled(self) -> set[str]:
        if not self._disabled_file.exists():
            return set()
        return {line.strip() for line in self._disabled_file.read_text(encoding="utf-8").splitlines() if line.strip()}