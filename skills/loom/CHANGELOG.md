# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [0.3.0] — 2026-03-22 — "Trust, But Verify"

The hardening release. Policy engine, crash recovery, memory decay, and performance benchmarks.

### Added

#### Policy Engine
- `loom policy install` — install default YAML policy into workspace
- `loom policy check <tool>` — preview what policy would decide
- YAML rule evaluation on every gateway tool call (deny blocks execution)
- Condition matching: `path_match`, `command_match`, `alias_match`
- Decisions: `allow`, `deny`, `approve` with reasons logged to events
- No PyYAML dependency — built-in minimal YAML parser

#### Crash Recovery
- `loom repair` — integrity check (7 checks) + auto-repair
  - Cleans expired write tokens
  - Closes stale sessions (>24h)
  - Rebuilds FTS5 index if out of sync with memory table
- `loom rebuild` — reconstruct memory.db from events.jsonl (nuclear option)
  - Replays `decision_logged` and `memory_written` events
  - Backs up corrupt memory.db before rebuilding

#### Memory Decay
- `loom decay --ttl 30` — auto-obsolete unvalidated hypotheses older than TTL
- `loom decay --dry-run` — preview what would be decayed
- Only affects `hypothesis` status — validated/obsolete/rejected untouched

#### Benchmark Suite
- `loom benchmark` — run init, write, search, handoff, and event benchmarks
- `loom benchmark --json` — machine-readable output
- Reports p50/p95/p99 latencies for every operation
- Search p95 verified under 10ms on 500 entries

#### Dockerfile
- Dockerfile updated to use `loom gateway start` as entrypoint
- docker-compose.yaml with persistent volume and healthcheck
- `pip install .[gateway]` installs Starlette + uvicorn

### Changed
- Gateway now evaluates policy before dispatching tool calls
- All new commands support `--json` flag

## [0.2.0] — 2026-03-22 — "Switch Models, Keep the Thread"

The cross-model handoff release.

### Added
- Session/actor model: `loom session open/close/list/cleanup`
- Write token: `loom token acquire/release/status` (lease-based exclusion)
- Import/export: `loom import CLAUDE.md`, `loom export claude-md`
- Context CLI: `loom context --json --save`
- Promote/reject: `loom promote <id>`, `loom reject <id> -r "reason"`
- Remote gateway: `loom gateway start` (SSE/HTTP + REST API + Bearer auth)
- Docker volume restore on `loom resume`
- `--json` flag on state, doctor, search, events, resume
- MCP tools: `loom_open_session`, `loom_close_session` (8 total)
- Cross-model handoff E2E test (Claude Code → Cursor → Windsurf)

## [0.1.0] — 2026-03-22 — "Never Start From Scratch Again"

First release. Memory layer, CLI, and MCP server.

### Added
- CLI: init, resume, doctor, state, connect, search, log, events, mcp serve
- MCP server with 6 tools over stdio transport
- SQLite + FTS5 memory with typed records and status model
- Runtime identity computation, append-only event log
- Setup guides for Claude Code, Cursor, Windsurf, Claude Desktop, Claude.ai, ChatGPT, Gemini
