# Roadmap

## Done (V0.1 — Foundations)

- [x] `loom init` — workspace initialization with project type detection
- [x] `loom resume` — verify identity, restore Docker cache volumes
- [x] `loom doctor` — 7-check health diagnostics
- [x] `loom connect` — auto-configure MCP for Claude Code, Cursor, Windsurf
- [x] `loom state` / `loom search` / `loom log` / `loom events` — CLI
- [x] MCP memory server (SQLite + FTS5) via stdio — 6 tools
- [x] Append-only event log (JSONL), runtime identity, DevContainer template
- [x] `--json` flag on all data commands, integration tests (28 E2E)

## Done (V0.2 — Sequential Handoff)

- [x] Session/actor model: open, close, list, cleanup
- [x] Write token: lease-based single-writer exclusion
- [x] Import/export: CLAUDE.md, .cursorrules, markdown
- [x] Promote/reject: hypothesis → validated / rejected
- [x] `loom context` CLI with --json and --save
- [x] Remote gateway (SSE/HTTP) with REST API and Bearer auth
- [x] MCP tools: loom_open_session, loom_close_session (8 total)
- [x] Cross-model handoff E2E test (Claude Code → Cursor → Windsurf)

## Done (V0.3 — Hardening)

- [x] Policy engine: YAML rules evaluated on every gateway tool call
- [x] Crash recovery: integrity check (7 checks), auto-repair, FTS5 rebuild
- [x] State rebuild: reconstruct memory.db from events.jsonl
- [x] Memory decay: auto-obsolete unvalidated hypothesis entries past TTL
- [x] Benchmark suite: init, write, search (p50/p95/p99), handoff, events
- [x] Dockerfile tested with gateway entrypoint + docker-compose with healthcheck

## Next (V1.0 — The Workspace Standard)

- [ ] Contract tests for all MCP tools (schema validation, breaking change detection)
- [ ] Compatibility matrix (Linux, macOS, Windows × Python 3.11–3.13)
- [ ] PyPI publication (`pip install loom`)
- [ ] Hybrid topology (local runtime + remote memory sync)
- [ ] OAuth authentication (beyond API keys)
- [ ] Rate limiting on gateway endpoints
- [ ] Reference demos published in CI

## Future (V2.0–V3.0)

- [ ] Git worktree-based parallel tracks
- [ ] Role-based actors (builder, reviewer, auditor)
- [ ] Policy-driven task routing
- [ ] Compound multi-agent workflows
- [ ] Enterprise features (SSO, RBAC, audit export)
- [ ] Managed SaaS option

## Not Planned

- ❌ Visual IDE or GUI editor
- ❌ Cloud-hosted model training or fine-tuning
- ❌ General-purpose task automation (Zapier/n8n replacement)
- ❌ Browser extension or web app (V1)
- ❌ Proprietary protocol (MCP only)
- ❌ Multi-tenant SaaS before V3.0
