# Roadmap

## Done (V0.1 — Foundations)

- [x] `loom init` — workspace initialization with project type detection
- [x] `loom resume` — verify identity, restore Docker cache volumes
- [x] `loom doctor` — 7-check health diagnostics
- [x] `loom connect` — auto-configure MCP for Claude Code, Cursor, Windsurf
- [x] `loom state` — workspace snapshot (identity, memory, events, git)
- [x] `loom search` / `loom log` / `loom events` — memory CLI
- [x] MCP memory server (SQLite + FTS5) via stdio — 6 tools
- [x] Append-only event log (JSONL)
- [x] DevContainer template generation
- [x] Runtime identity computation and manifest
- [x] `--json` flag on all data commands
- [x] Integration tests (28 E2E via subprocess)

## Done (V0.2 — Sequential Handoff)

- [x] Session and actor model (open/close/list/cleanup)
- [x] Write token management (lease-based single-writer exclusion)
- [x] `loom_get_handoff_summary` — structured transfer packets
- [x] `loom context` — compact project onboarding (Rich, JSON, save)
- [x] `loom import` / `loom export` — CLAUDE.md and .cursorrules migration
- [x] `loom promote` / `loom reject` — memory status management
- [x] Cross-model handoff E2E test (Claude Code → Cursor → Windsurf)
- [x] MCP tools: `loom_open_session`, `loom_close_session` (8 tools total)
- [x] Remote gateway (SSE/HTTP) with REST API and Bearer auth
- [x] Docker volume restore on `loom resume`

## Next (V0.3 — Hardening)

- [ ] Policy engine (evaluate YAML rules on every tool call)
- [ ] Dockerfile tested end-to-end with gateway
- [ ] Crash recovery (stale session cleanup on resume, integrity checks)
- [ ] State rebuild from events.jsonl (`loom rebuild`)
- [ ] Memory decay (auto-obsolete unvalidated entries past TTL)
- [ ] Benchmark suite (`loom benchmark` — init, search, handoff latency)
- [ ] Rate limiting on gateway endpoints

## Later (V1.0 — The Workspace Standard)

- [ ] Contract tests for all MCP tools (schema validation)
- [ ] Compatibility matrix (Linux, macOS, Windows × Python 3.11–3.13)
- [ ] PyPI publication (`pip install loom`)
- [ ] Hybrid topology (local runtime + remote memory sync)
- [ ] OAuth authentication (beyond API keys)
- [ ] Reference demos and benchmarks published in CI

## Future (V2.0–V3.0)

- [ ] Git worktree-based parallel tracks
- [ ] Role-based actors (builder, reviewer, auditor)
- [ ] Policy-driven task routing
- [ ] Compound multi-agent workflows
- [ ] Enterprise features (SSO, RBAC, audit export)
- [ ] Managed SaaS option

## Not Planned

These are explicitly out of scope to resist feature creep:

- ❌ Visual IDE or GUI editor
- ❌ Cloud-hosted model training or fine-tuning
- ❌ General-purpose task automation (Zapier/n8n replacement)
- ❌ Browser extension or web app (V1)
- ❌ Proprietary protocol (MCP only)
- ❌ Multi-tenant SaaS before V3.0
