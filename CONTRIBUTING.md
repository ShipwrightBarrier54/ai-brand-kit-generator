# Contributing to ai-brand-kit-generator

Thanks for wanting to help build the brand kit generator. This is a 2026-era
Windows desktop tool that turns a short brand brief into a full asset kit:
logo concepts, palettes, typography pairings, voice guidelines, and export
bundles.

## Dev setup

```powershell
git clone https://github.com/yourorg/ai-brand-kit-generator.git
cd ai-brand-kit-generator
py -3.12 -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -e ".[dev]"
pre-commit install
```

Python 3.11+ is the floor. 3.12 is what CI runs. We test on Windows 11
22H2+ and Windows Server 2022. Linux/macOS dev is best-effort and not
supported for the GUI layer.

## Layout

```
ai_brand_kit/          # main package
  cli/                 # command-line entry points
  core/                # orchestration + pipeline
  generators/          # per-asset generators (logo, palette, type, voice)
  services/            # external services (model inference, font fetch, export)
  models/              # dataclasses + pydantic schemas
  utils/               # shared helpers
  config/              # default configs, presets, templates
tests/                 # pytest suite
docs/                  # design notes
```

## Style

- `ruff` for lint + format. Line length 100.
- `mypy --strict` on `ai_brand_kit/core` and `ai_brand_kit/generators`.
- No `print()` in library code — use the `logging` module.
- Public functions get type hints. Internal helpers can skip them if the
  signature is obvious.

## Adding a new generator

1. Drop a module in `ai_brand_kit/generators/`.
2. Subclass `BaseGenerator` from `ai_brand_kit/generators/base.py`.
3. Register it in `ai_brand_kit/generators/registry.py`.
4. Add a fixture brief in `tests/fixtures/briefs/` and a test in
   `tests/test_generators.py`.

## PRs

- One feature per PR. Rebase, don't merge.
- Include a test that fails before your change and passes after.
- Update `docs/architecture.md` if you touch the pipeline.

## Reporting bugs

Open an issue with the brief that triggered it (redact anything sensitive),
the generated kit hash, and the traceback. Attach `brandkit.log` if you can.