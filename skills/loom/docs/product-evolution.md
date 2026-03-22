# Product Evolution V0.1 – V3.0

Each phase delivers a usable result, validates a distinct hypothesis, and has its own marketing narrative.

## V0.1 — Foundations

> **"Never Start From Scratch Again"**
> Your AI workspace remembers. Resume in seconds, not minutes.

**Goal:** Prove that a workspace can be resumed without restarting the world.

**Timeline:** 6 weeks

### Must Include
- Workspace initialization with project type detection (Python, Node, Rust, Go)
- Deterministic runtime identity (hash of devcontainer.json + lockfiles + tool versions)
- Inventory refresh (SQLite-backed file index)
- Append-only event log (JSONL)
- Doctor and repair flows
- Runtime persistence via named Docker volumes
- MCP memory server (SQLite + FTS5) — local stdio
- Client connector (`loom connect claude-code|cursor|windsurf`)
- CLI commands: init, resume, doctor, state, connect, repair, test

### Must Avoid
- No concurrency beyond single active writer
- No remote gateway
- No vector search (FTS5 only)
- No TUI dashboard
- No plugin/extension system

### Exit Criteria
- Users can close, return, run `loom resume`, and recover in <30 seconds
- A model connected via MCP can search memory and read handoff summaries

---

## V0.2 — Sequential Model Handoff

> **"Switch Models, Keep the Thread"**
> Work with Claude today, switch to GPT tomorrow. Your project doesn't care which AI you use.

**Goal:** Prove that one model can resume another model's work without full project rediscovery.

**Timeline:** +4 weeks (week 10)

### Must Include
- Actor and session model (open/close/attach)
- Shared project memory + private session memory
- Handoff summary generation
- `loom context` — compact project onboarding file
- `loom import` / `loom export` — CLAUDE.md migration
- Mini dashboard (CLI-rendered)

### Must Avoid
- No simultaneous writing
- No remote model access
- No advanced dependency impact blocker

### Exit Criteria
- A second model resumes useful work with materially less prompt scaffolding
- Import from CLAUDE.md and export back both work

---

## V0.3 — Controlled Gateway + Remote Access

> **"Your Workspace, Accessible from Anywhere"**
> Connect Claude.ai, ChatGPT, or any AI to your project — from the cloud, with guardrails.

**Goal:** Allow remote models to use the workspace through an explicit, inspectable control surface.

**Timeline:** +6 weeks (week 16)

### Must Include
- MCP gateway with SSE/HTTPS transport
- API key authentication
- YAML-based policy engine (allow/deny/approve)
- Approval hooks in CLI
- Gateway event tracing
- Multi-project support (`loom_set_project`)
- Deployment template (Dockerfile + docker-compose)

### Must Avoid
- No cloud-initiated direct machine ingress
- No permanently open sessions
- No unrestricted shell for remote clients

### Exit Criteria
- Remote model writes decisions and reads summaries via HTTPS
- Every action is audited and policy-gated

---

## V0.4 — Memory & Recovery Hardening

**Goal:** Make memory and reconstruction genuinely useful rather than merely present.

**Timeline:** +6 weeks (week 22)

### Must Include
- Memory status model with promotion flows
- Crash recovery and stale session cleanup
- State rebuild from repo + events (tolerate partial .loom/ loss)
- OAuth 2.0 support for remote topology
- Rate limiting per client
- Dependency mapping (language-specific adapters)

### Exit Criteria
- Recovery is trusted after .loom/ corruption
- Memory helps more often than it misleads

---

## V1.0 — Stable Technical Substrate

> **"The Workspace Standard"**
> The open standard for AI-assisted workspaces. Persistent. Inspectable. Transferable. Governed.

**Goal:** Freeze core contracts and make the project publishable as a serious open-source base.

**Timeline:** +4 weeks (week 26 / month 6)

### Must Include
- Stable CLI and MCP gateway contracts (with contract tests)
- Published architecture and threat model
- Compatibility matrix (Linux, macOS, Windows; Claude Code, Cursor, Windsurf)
- Hybrid topology (local-remote sync)
- Reference demos (Python + Node/TS projects)
- Published benchmarks
- Claude.ai skill template

### Exit Criteria
- Third parties can install, evaluate, contribute, and report issues with minimal guidance

---

## V2.0 — Parallel Work Streams

> **"The Forge Ignites"**
> Multiple AI agents, one project, zero chaos. The Forge is open.

**Goal:** Introduce safe parallelism through isolation.

**Timeline:** +12 weeks (month 9)

### Must Include
- Git worktree-backed execution tracks
- Role split: writer, reviewer, auditor
- Cross-track diff and merge (test-gated)
- Team RBAC for remote topology

### Exit Criteria
- Parallelism is useful because isolated and reviewable, not because uncontrolled

---

## V3.0 — Coordinated Actor Ecosystem

> **"Orchestrated Intelligence"**
> Specialized AI roles. Policy-driven routing. Compound workflows. The OS for AI-assisted engineering.

### Must Include
- Specialized actor roles (builder, reviewer, auditor, release operator)
- Policy-driven task routing
- Compound workflows across build, docs, review, release
- Enterprise features (SSO, RBAC, audit export)
- Managed SaaS option

### Must Avoid
- No hidden autonomous system that bypasses approvals
- No assumption that more actors always improve outcomes
- Benchmark every orchestration claim against the simpler sequential baseline
