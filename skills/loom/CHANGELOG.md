# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [0.2.0] — 2026-03-22 — "Switch Models, Keep the Thread"

The cross-model handoff release. Sessions, write tokens, import/export, and a remote gateway.

### Added

#### Session & Actor Model
- `loom session open <actor>` — track which AI tool is working
- `loom session close` — end session with optional summary
- `loom session list` — view session history with actors and models
- `loom session cleanup` — auto-close stale sessions (>24h)
- MCP tools: `loom_open_session`, `loom_close_session`
- Sessions table in SQLite, persists in `memory.db`

#### Write Token (Single-Writer Exclusion)
- `loom token acquire <session_id> <actor>` — lease-based write lock
- `loom token release <session_id>` — release the lock
- `loom token status` — check who holds the token
- Configurable lease duration (default 15 min), auto-expire, `--force` reclaim

#### Import / Export
- `loom import CLAUDE.md` — import decisions and conventions from markdown
- `loom import .cursorrules` — import from Cursor rules (JSON or plain text)
- `loom export claude-md` — export validated decisions as CLAUDE.md
- `loom export markdown` — full memory dump as readable markdown

#### Context CLI
- `loom context` — compact project overview (goals, decisions, risks)
- `loom context --json` — machine-readable output
- `loom context --save` — write `.loom/context.md` for non-MCP tools

#### Promote / Reject
- `loom promote <id>` — hypothesis → validated
- `loom reject <id> -r "reason"` — hypothesis → rejected

#### Remote Gateway (SSE/HTTP)
- `loom gateway start` — SSE/HTTP server on configurable port
- `loom gateway keygen` — generate secure API key
- REST API: `/api/search`, `/api/log-decision`, `/api/handoff`, `/api/context`, `/api/write-memory`
- MCP-over-HTTP: `/mcp/messages` (JSON-RPC)
- Bearer token authentication via `LOOM_API_KEY`

#### Docker & DevContainer
- `loom resume` now detects Docker and restores cache volumes
- `loom gateway devcontainer` — generate devcontainer.json with cache volumes

#### --json Flag
- Added to: `state`, `doctor`, `search`, `events`, `resume`, `context`, `session list`, `token status`

#### Testing
- 104 tests (73 unit + 31 integration), test/source ratio 49%
- Cross-model handoff E2E test: Claude Code → Cursor → Windsurf

### Changed
- MCP server expanded from 6 to 8 tools
- `loom resume` enhanced with Docker cache restore

## [0.1.0] — 2026-03-22 — "Never Start From Scratch Again"

First release. Memory layer, CLI, and MCP server.

### Added
- CLI: `init`, `resume`, `doctor`, `state`, `connect`, `search`, `log`, `events`, `mcp serve`
- MCP server with 6 tools over stdio transport
- SQLite + FTS5 memory with typed records and status model
- Runtime identity computation (SHA-256 of lockfiles)
- Append-only event log (JSONL)
- FTS5 query sanitization, thread-safe SQLite (WAL mode)
- 21 documentation files, 4 ADRs, JSON schemas
- Setup guides for Claude Code, Cursor, Windsurf, Claude Desktop, Claude.ai, ChatGPT, Gemini
- Docker deployment configs, example project
