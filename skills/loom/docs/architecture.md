# Architecture

## Overview

Loom is organized into five pillars, each responsible for a distinct concern. The pillars communicate through defined interfaces and share a common event bus (the JSONL event log).

## Five Pillars

### P1: Runtime Shell
**Responsibility:** Container lifecycle, cache persistence, runtime identity, environment rebuild.

**Technology:** Docker + DevContainers spec. Named volumes for package caches (pip, npm, cargo). Python CLI (Click + Rich) for lifecycle commands (`init`, `resume`, `doctor`, `repair`).

**Key design:** The runtime identity is a deterministic SHA-256 hash of the environment definition (devcontainer.json + lockfiles + tool versions). This hash is used to detect drift and decide whether a fast resume is possible or a rebuild is needed.

**Boundary:** P1 owns everything related to "is the environment functional?" It does not know about memory, sessions, or policies.

### P2: Project Memory
**Responsibility:** Structured decision records, artifact references, handoff summaries, searchable project history.

**Technology:** SQLite embedded DB (`.loom/memory.db`). FTS5 for full-text search. Typed records with a status model (hypothesis → validated → obsolete → rejected). Optional sqlite-vss for vector similarity search (V0.4+).

**Key design:** Memory is consultative, never authoritative. If memory contradicts filesystem or Git, the filesystem and Git win. Memory accelerates and explains — it does not become a parallel source of truth.

**Boundary:** P2 owns everything related to "what do we know about this project?" It does not execute commands or manage containers.

### P3: State Index
**Responsibility:** File inventory, service detection, workspace health snapshots, change tracking, event log.

**Technology:** SQLite for file inventory (`.loom/inventory.db`). Append-only JSONL for events (`.loom/events.jsonl`). Git-derived diffs for change tracking.

**Key design:** The event log is append-only and records every significant action. It serves both as an audit trail and as a reconstruction source — if `.loom/memory.db` is lost, decisions can be replayed from events.

**Boundary:** P3 owns "what does the workspace look like right now?" and "what happened?" It does not make decisions or enforce policies.

### P4: MCP Gateway
**Responsibility:** Controlled tool surface for local and remote AI clients. Protocol handling. Authentication. Authorization. Policy engine. Audit.

**Technology:** MCP server supporting stdio (local) and SSE/HTTPS (remote). YAML-based policy files. JWT/API key authentication. Per-call audit logging to the event bus.

**Key design:** The gateway is the single entry point for all model interactions. Every tool call passes through: authentication → session validation → policy evaluation → dispatch → audit. This applies identically whether the client is local (Claude Code via stdio) or remote (Claude.ai via SSE).

**Boundary:** P4 owns "who is allowed to do what?" It delegates actual work to P1, P2, and P3.

### P5: Coordination
**Responsibility:** Sessions, actors, write tokens, worktrees, parallel execution tracks.

**Technology:** Sequential one-writer model in V0.x–1.0 (write token with lease semantics). Git worktrees as isolation units in V2.0+. Role-based actor model in V3.0. Potential Rust rewrite for CLI if performance becomes critical.

**Key design:** Coordination is deliberately deferred. V0.x proves that a sequential model with good handoff is more valuable than premature concurrency. V2.0 introduces parallelism only through isolation (separate worktrees), never through shared-directory multi-writing.

**Boundary:** P5 owns "who is working right now and how do they coordinate?" It does not own what they're working on.

## Deployment Topologies

| Topology | Transport | P1 Runtime | P2 Memory | P3 State | P4 Gateway | When |
|----------|-----------|:----------:|:---------:|:--------:|:----------:|------|
| **A. Local** | stdio | ✓ | ✓ | ✓ | ✓ (local) | V0.1 |
| **B. Remote** | SSE/HTTPS | Optional | ✓ | ✓ | ✓ (remote) | V0.3 |
| **C. Hybrid** | Both | ✓ (local) | ✓ (remote) | ✓ (both) | ✓ (both) | V1.0 |

In remote topology, P1 (Runtime Shell) may not be present — a cloud Loom instance can operate as pure memory + governance without Docker. This makes Loom deployable as a lightweight service on Fly.io, Railway, or even serverless (with a storage adapter).

## State Model

The filesystem expresses the live project. Git expresses committed lineage. `.loom/` expresses accelerated knowledge.

| Layer | Type | Role | Reconciliation Rule |
|-------|------|------|-------------------|
| Filesystem | Canonical | Current project content | Always wins |
| Git | Canonical | Versioned lineage | Primary rollback reference |
| `.loom/inventory` | Derived | Fast state index | Rebuildable from filesystem |
| `.loom/memory` | Derived | Decision records | Rebuildable from events + Git |
| `.loom/events` | Derived (critical) | Audit + reconstruction | Append-only, never modified |
| Gateway | Operational | Controlled execution surface | Stateless (config-driven) |

**If divergence occurs:** Loom reconciles toward filesystem and Git, never toward `.loom/`. The derived state is disposable and reconstructible.

## Invariants

These rules are architectural constraints that must hold at all times. Changes require an RFC.

1. **One active writer** per workspace in V0.x–V1.0. Write token is lease-based with expiration.
2. **Explicit sessions** required before any remote execution is permitted.
3. **Everything evented** — every stateful action (file write, command execution, decision logged, session opened) is recorded in `events.jsonl`.
4. **Policy-gated sensitive actions** — file writes, shell execution, secret access, and dependency installation pass through the policy engine.
5. **Reconstructible `.loom/`** — must be rebuildable to an acceptable baseline from filesystem + Git + event history.
6. **Deterministic runtime identity** — must detect incompatible reuse and refuse silent cache restoration.
7. **MCP-native** — all model-facing interactions use standard MCP protocol. No custom wire formats.

## Diagram

```
┌───────────────────────────────────────────────────────────────┐
│  CLIENTS: Claude Code  Cursor  Windsurf  Claude.ai  ChatGPT  │
│           (stdio)     (stdio)  (stdio)   (SSE)      (SSE)    │
└───────────────────────┬───────────────────────────────────────┘
                        ▼
┌───────────────────────────────────────────────────────────────┐
│   P4: MCP GATEWAY  (Auth + Policy + Routing + Audit)         │
└───────────────────────────────────────────────────────────────┘
            ▼                  ▼                  ▼
┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐
│ P2: PROJECT     │  │ P3: STATE       │  │ P1: RUNTIME     │
│ MEMORY          │  │ INDEX           │  │ SHELL           │
│ SQLite + FTS5   │  │ Git + JSONL     │  │ Docker+Volumes  │
└─────────────────┘  └─────────────────┘  └─────────────────┘
                        ▼
┌───────────────────────────────────────────────────────────────┐
│  WORKSPACE: Filesystem + Git + .loom/ (canonical truth)       │
└───────────────────────────────────────────────────────────────┘
```
