"""Typer CLI for ai-brand-kit-generator.

Subcommands:
  generate   run the full pipeline from a brief file or inline flags
  inspect    dump the parsed brief and resolved config
  plugins    list / enable / disable installed generator plugins
  doctor     check environment (fonts, model cache, export dirs)
"""
from __future__ import annotations

import json
import logging
from pathlib import Path

import typer
from rich.console import Console
from rich.table import Table

from ai_brand_kit import __version__
from ai_brand_kit.core.pipeline import BrandKitPipeline
from ai_brand_kit.core.plugin_loader import PluginLoader
from ai_brand_kit.models.brief import BrandBrief
from ai_brand_kit.utils.logging_setup import configure_logging

app = typer.Typer(
    name="brandkit",
    help="Generate a full brand kit from a short brief.",
    no_args_is_help=True,
    add_completion=False,
)
console = Console()
log = logging.getLogger("ai_brand_kit.cli")


@app.command()
def generate(
    brief: Path = typer.Option(..., "--brief", "-b", exists=True, dir_okay=False),
    out: Path = typer.Option(Path("generated_kits"), "--out", "-o"),
    preset: str = typer.Option("default", "--preset", "-p"),
    seed: int | None = typer.Option(None, "--seed"),
    verbose: bool = typer.Option(False, "--verbose", "-v"),
) -> None:
    """Run the full brand kit pipeline from a brief file."""
    configure_logging(verbose)
    brief_model = BrandBrief.from_file(brief)
    pipeline = BrandKitPipeline(preset=preset, seed=seed)
    kit = pipeline.run(brief_model, out_dir=out)
    console.print(f"[bold green]kit written[/] -> {kit.root}")
    console.print(f"assets: {len(kit.assets)}  warnings: {len(kit.warnings)}")


@app.command()
def inspect(
    brief: Path = typer.Option(..., "--brief", "-b", exists=True, dir_okay=False),
) -> None:
    """Parse a brief and print the resolved model."""
    model = BrandBrief.from_file(brief)
    console.print_json(model.model_dump_json(indent=2))


@app.command("plugins")
def plugins_cmd(
    action: str = typer.Argument("list", help="list | enable | disable"),
    name: str | None = typer.Argument(None),
) -> None:
    """Manage generator plugins."""
    loader = PluginLoader()
    if action == "list":
        table = Table("name", "version", "enabled", "path")
        for p in loader.discover():
            table.add_row(p.name, p.version, str(p.enabled), str(p.path))
        console.print(table)
    elif action in {"enable", "disable"} and name:
        loader.set_enabled(name, action == "enable")
        console.print(f"{name}: {action}d")
    else:
        raise typer.BadParameter("usage: plugins [list|enable|disable] [name]")


@app.command()
def doctor() -> None:
    """Check environment health."""
    from ai_brand_kit.services.fonts import FontRegistry

    checks: dict[str, str] = {}
    checks["version"] = __version__
    checks["fonts"] = f"{len(FontRegistry.default().families())} families"
    checks["export_dir"] = str(Path("generated_kits").resolve())
    console.print_json(json.dumps(checks))


@app.callback()
def _root() -> None:
    """ai-brand-kit-generator CLI."""