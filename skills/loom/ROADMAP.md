# Roadmap

## Now (V0.1 — Foundations)

- [ ] `loom init` — workspace initialization with project type detection
- [ ] `loom resume` — restore workspace from manifests and cached volumes
- [ ] `loom doctor` — health checks with structured diagnostics
- [ ] `loom connect` — generate MCP config for Claude Code, Cursor, Windsurf
- [ ] `loom state` — workspace status snapshot
- [ ] MCP memory server (SQLite + FTS5) via stdio
- [ ] Append-only event log (JSONL)
- [ ] DevContainer reference template
- [ ] Runtime identity computation and manifest

## Next (V0.2 — Sequential Handoff)

- [ ] Actor and session model (open/close/attach)
- [ ] Write token management (lease-based)
- [ ] `get_handoff_summary` — structured transfer packets
- [ ] `loom context` — compact project onboarding file
- [ ] `loom import` / `loom export` — CLAUDE.md migration
- [ ] Cross-model handoff validation

## Later (V0.3–V1.0)

- [ ] MCP gateway with SSE/HTTPS transport (remote access)
- [ ] Policy engine (YAML-based rules)
- [ ] Authentication (API key → OAuth)
- [ ] Memory status model (hypothesis → validated → obsolete)
- [ ] Crash recovery and state rebuild
- [ ] Hybrid topology (local + remote sync)
- [ ] Stable contracts with contract tests
- [ ] Compatibility matrix (Linux, macOS, Windows)
- [ ] Reference demos and benchmarks

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
