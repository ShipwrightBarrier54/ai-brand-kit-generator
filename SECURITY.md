# Security Policy

## Supported versions

| Version | Supported |
| ------- | --------- |
| 0.4.x   | yes       |
| 0.3.x   | security fixes only |
| < 0.3   | no        |

## Reporting a vulnerability

Email `security@ai-brand-kit-generator.dev` with a description, a
reproduction, and the affected version. Do not open a public issue for
anything that looks like a real vulnerability. We aim to acknowledge
within 72 hours and ship a fix within 14 days for high-severity issues.

## Scope

In scope:
- Arbitrary code execution via crafted brand briefs, font files, or
  preset YAML.
- Path traversal in the export bundler (`ai_brand_kit/services/exporter.py`).
- SSRF or credential leakage via the model inference adapter when a
  custom `inference_endpoint` is configured.
- Dependency confusion in the plugin loader (`ai_brand_kit/core/plugin_loader.py`).

Out of scope:
- Prompt-injection against the local model that only produces a weird
  brand kit. That's a content bug, not a security bug.
- Anything requiring the attacker to already have local code execution.

## Hardening notes for users

- Run the generator with a dedicated low-privilege Windows account.
- Do not point `inference_endpoint` at untrusted hosts.
- Font files are parsed with `fonttools`; keep it pinned and updated.
- The plugin loader only loads from `%APPDATA%\ai-brand-kit-generator\plugins`
  by default. Do not add untrusted directories to `plugin_paths`.