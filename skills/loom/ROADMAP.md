# Roadmap

## Done (V0.1 — Foundations)

- [x] CLI: init, resume, doctor, state, connect, search, log, events, mcp serve
- [x] MCP server (6 tools), SQLite+FTS5, event log, runtime identity
- [x] `--json` flag, integration tests (28 E2E)

## Done (V0.2 — Sequential Handoff)

- [x] Sessions, write token, import/export, promote/reject, context CLI
- [x] Remote gateway (SSE/HTTP + REST + Bearer auth), MCP expanded to 8 tools
- [x] Cross-model handoff E2E test (Claude Code → Cursor → Windsurf)

## Done (V0.3 — Hardening)

- [x] Policy engine, crash recovery, state rebuild, memory decay
- [x] Benchmark suite, Dockerfile with gateway entrypoint

## Done (V0.4 — Adoptable)

- [x] Interactive `loom init` (template + auto-import + auto-connect)
- [x] 7 project templates (web-backend, frontend, mobile, data, cli, infra, library)
- [x] `loom status` one-liner (state+doctor+session+token+team)
- [x] Team mode: multi-user auth with roles (admin/member/viewer)
- [x] Multi-workspace router with per-project URL routing
- [x] PyPI-ready pyproject.toml + GitHub Action for publishing

## Next (V0.5 — Indispensable)

- [ ] Semantic search (embeddings complement to FTS5)
- [ ] `loom diff` between sessions (what changed since last handoff?)
- [ ] Smart handoff (contextualized summary, not raw dump)
- [ ] Memory hooks / webhooks (Slack notification on risk, email on promote)
- [ ] `loom watch` daemon (live workspace monitoring)

## Later (V1.0 — The Workspace Standard)

- [ ] Contract tests for all 8 MCP tools
- [ ] Compatibility matrix (Linux, macOS, Windows × Python 3.11-3.13)
- [ ] PyPI publication (`pip install loom`)
- [ ] Hybrid topology (local runtime + remote memory sync)
- [ ] OAuth2 authentication

## Future (V2.0–V3.0)

- [ ] PostgreSQL backend (>20 concurrent users)
- [ ] Git worktree-based parallel tracks
- [ ] Role-based actors (builder, reviewer, auditor)
- [ ] MCP Hub (proxy + aggregate multiple MCP servers)
- [ ] Compliance mode (signed audit trail)
- [ ] Enterprise features (SSO, RBAC, audit export)

## Not Planned

- ❌ Visual IDE or GUI editor
- ❌ Cloud-hosted model training
- ❌ General-purpose automation (Zapier/n8n)
- ❌ Proprietary protocol (MCP only)
- ❌ Multi-tenant SaaS before V3.0
