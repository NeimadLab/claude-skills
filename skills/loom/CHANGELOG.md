# Changelog

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/).

## [0.4.0] — 2026-03-22 — "Adoptable"

One-command onboarding. Templates. Status dashboard. PyPI-ready.

### Added
- `loom init` is now interactive: offers templates, auto-imports CLAUDE.md/.cursorrules, auto-connects AI tool
- `loom init --template web-backend` applies domain templates in non-interactive mode
- `loom init --non-interactive` for CI/CD and scripting
- `loom status` — one-screen dashboard: state + doctor + session + token + team mode
- `loom templates list` / `loom templates apply <name>` — manage project templates
- 7 built-in templates: web-backend, web-frontend, mobile-app, data-pipeline, cli-tool, infra-devops, library
- `loom team add/list/remove/limits` — multi-user auth with roles (admin/member/viewer)
- `loom workspace register/list/remove/serve` — multi-workspace gateway
- PyPI publish GitHub Action (.github-pypi/publish.yml)
- pyproject.toml: project URLs, Python 3.13 classifier, Beta status

### Changed
- `loom connect` refactored to use shared helper (also used by interactive init)

## [0.3.0] — 2026-03-22 — "Trust, But Verify"

Policy engine, crash recovery, memory decay, benchmarks.

### Added
- Policy engine: `loom policy install/check`, YAML rules, gateway integration
- Recovery: `loom repair` (integrity + auto-fix), `loom rebuild` (from events.jsonl)
- Memory decay: `loom decay --ttl 30 --dry-run`
- Benchmarks: `loom benchmark --json` (p50/p95/p99)
- Dockerfile tested with gateway entrypoint

## [0.2.0] — 2026-03-22 — "Switch Models, Keep the Thread"

Sessions, write tokens, import/export, remote gateway.

### Added
- Session/actor model, write token (lease-based), import/export, promote/reject
- Remote gateway (SSE/HTTP + REST API + Bearer auth)
- MCP tools: loom_open_session, loom_close_session (8 total)
- Cross-model handoff E2E test

## [0.1.0] — 2026-03-22 — "Never Start From Scratch Again"

First release. Memory layer, CLI, MCP server.
