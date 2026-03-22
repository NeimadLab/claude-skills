<div align="center">

# Omni-Agent Forge — Project Bible v3

**Consolidated Charter, Architecture, Roadmap & Operations**

*March 2026*

</div>

---

**Table of Contents**

1. [Problem Statement & Value Proposition](#1-problem-statement--value-proposition)
2. [Architecture & Technology](#2-architecture--technology)
3. [Product Evolution V0.1–V3.0](#3-product-evolution-v01--v30)
4. [Detailed Function & Skill Catalog](#4-detailed-function--skill-catalog)
5. [Repository Structure & Contributor Guide](#5-repository-structure--contributor-guide)
6. [Risks, Anti-Patterns & Mitigations](#6-risks-anti-patterns--mitigations)
7. [Brand, Communication & Community](#7-brand-communication--community)
8. [Next Steps & Action Plan](#8-next-steps--action-plan)
9. [Annexes](#annexes)

---

# 1. Problem Statement & Value Proposition

## 1.1 The Five Friction Points

Current model-assisted workflows repeatedly lose operational value in five places. Each is documented by community experience in 2025–2026 and confirmed by tool comparison studies.

+––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––-+
**F1: Context Amnesia**
The model forgets practical context mid-session or across sessions. Claude Code compacts without warning, losing decisions made 90 minutes ago. Cursor fragments context across tabs. Windsurf degrades in long sessions. No tool has solved persistent project memory.
+––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––-+

+––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––+
**F2: Environment Rebuild Tax**
Every new session starts cold. Package reinstalls, configuration rediscovery, state reconstruction. Developers report 5–15 minutes of setup overhead per session restart. Multiplied by 3–5 restarts per day, this is 30–75 minutes of lost productivity daily.
+––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––+

+––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––-+
**F3: Cross-Model Blindness**
Developers increasingly use multiple AI tools (Claude Code for deep architecture, Cursor for daily coding, Windsurf for iterative flows). Context does not transfer between them. Each tool starts from zero. Manual copy-paste of brain state across tabs.
+––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––-+

+–––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––-+
**F4: Zero Governance**
Remote models accessing local filesystems have no standard policy framework. DevContainers provide isolation but not governance. No audit trail, no approval workflow, no secret protection. Every shell command is an ungoverned action.
+–––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––-+

+–––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––-+
**F5: No Handoff Protocol**
When one model hands off to another (or to the same model in a new session), there is no structured way to transfer: current goal, recent decisions, changed files, open risks, next actions. The handoff is either manual prompt engineering or nothing.
+–––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––-+

## 1.2 Who Suffers: Target Users

  –––––––––––––––– ––––––––––––––––––––––––––––––––––––––––––––––––––- ––––––––––––––––––––––––––––––––––––––- ––––––––––––––––––––––––––-
  **Segment**                      **Why They Care**                                                                                     **Current Workaround**                                                        **OAF Fit**

  **Solo technical builder**       Wants fast resume and fewer repeated setup cycles. Switches between Claude Code and Cursor daily.     Manual CLAUDE.md, copy-paste context, rebuild env each session.               Excellent. Primary V0.1–0.2 target.

  **Small engineering team**       Needs repeatable handoff, shared project knowledge, and consistent conventions across team members.   Shared docs, Notion pages, tribal knowledge. No structured handoff.           Strong. V0.3+ with remote topology and team memory.

  **AI-heavy product team**        Switches models frequently. Values throughput and model-agnostic workflows.                           Multiple tool subscriptions. Manual context bridging. Nucleus MCP for some.   Strong. Will push for remote + parallel early.

  **Enterprise / regulated org**   Needs audit trails, governance, approved model access, and controlled execution.                      Bespoke internal tooling or nothing. DevContainers for isolation only.        V1.0+ with policy engine, RBAC, audit export.
  –––––––––––––––– ––––––––––––––––––––––––––––––––––––––––––––––––––- ––––––––––––––––––––––––––––––––––––––- ––––––––––––––––––––––––––-

## 1.3 Competitive Landscape

No single tool covers all five friction points. OAF's strategic value is the integration layer.

  –––––––––––––- ––––––––––– ––––––––– ––––––––- –––––––– ––––––- –––––- ––––––
                              **Context Persist.**   **Env Persist.**   **Cross-Model**   **Governance**   **Handoff**   **Local**   **Remote**

  **Claude Code CLAUDE.md**   ✓                      ✗                  ✗                 ✗                ✗             ✓           ✗

  **Nucleus MCP**             ✓                      ✗                  ✓                 ✗                Partial       ✓           ✗

  **DevContainers**           ✗                      ✓                  ✗                 Partial          ✗             ✓           ✗

  **mem0 / OpenMemory**       ✓                      ✗                  ✓                 ✗                ✗             ✓           ✓

  **Windsurf Memories**       ✓                      ✗                  ✗                 ✗                ✗             ✓           ✗

  **LangGraph/CrewAI**        Partial                ✗                  ✗                 Partial          ✓             ✗           ✓

  **OAF (target)**            **✓**                  **✓**              **✓**             **✓**            **✓**         **✓**       **✓**
  –––––––––––––- ––––––––––– ––––––––– ––––––––- –––––––– ––––––- –––––- ––––––

## 1.4 Value Proposition

+–––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––-+
**OAF Value Proposition**
Omni-Agent Forge is the only workspace substrate that unifies runtime persistence, structured project memory, cross-model handoff, and governed access — local and remote, model-agnostic — so technical users can resume real work instead of rebuilding context every time.
+–––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––-+

## 1.5 Strategic Positioning & Timing

**Why now:** The window is 12–18 months. MCP is the new standard (late 2024). AI coding tools have proven their value but not solved persistence. Major vendors (Anthropic, GitHub, OpenAI) will eventually absorb these capabilities natively. OAF must establish itself as the neutral, open-source workspace standard before that happens. If absorbed, mission accomplished — the standard will have been set.

**What OAF should be:** A persistent workspace and runtime layer. A bridge across models, sessions, and deliverables. An inspectable system with explicit permissions. A contributor-friendly open-source technical product.

**What OAF should NOT be:** A vague all-purpose autonomous agent platform. A concurrency-first experiment with weak guarantees. A magical black box that hides state and authority. A large unscoped framework trying to support every workflow from day one.

# 2. Architecture & Technology

## 2.1 The Five Pillars

+––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––+
**P1: Runtime Shell**
**Scope:** Container lifecycle, cache persistence, runtime identity, environment rebuild
**Technology:** Docker + DevContainers spec. Named volumes for caches. Rust/Go CLI for lifecycle commands. devcontainer.json as config format.
+––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––+

+––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––-+
**P2: Project Memory**
**Scope:** Structured decisions, artifact refs, handoff summaries, searchable history
**Technology:** SQLite embedded DB (.oaf/memory.db). FTS5 for full-text search. Typed records with status model. Optional sqlite-vss for vector search (V0.4+).
+––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––-+

+–––––––––––––––––––––––––––––––––––––––––––––––––––––––––––+
**P3: State Index**
**Scope:** File inventory, service detection, workspace health, diff tracking, events
**Technology:** SQLite for inventory. Append-only JSONL for events. Git-derived diffs. Lightweight, reconstructible.
+–––––––––––––––––––––––––––––––––––––––––––––––––––––––––––+

+––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––+
**P4: MCP Gateway**
**Scope:** Controlled tool surface for local and remote AI clients. Policy engine. Auth. Audit.
**Technology:** MCP server: stdio (local) + SSE/HTTPS (remote). YAML-based policy files. JWT/API key auth. Per-call audit logging.
+––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––+

+––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––+
**P5: Coordination**
**Scope:** Sessions, actors, write tokens, worktrees, parallel tracks
**Technology:** Deferred to V2.0+ for parallel. Sequential one-writer model in V0.x–1.0. Git worktrees as isolation unit.
+––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––+

## 2.2 Deployment Topologies

  ––––––––––––––––– –––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––– ––––––––––––––––––––––––––––––––––––––––––––––––
  **Topology**                       **How It Works**                                                                                                                                                         **Use Cases**

  **A. Local-Only (V0.1 default)**   OAF runs as local CLI + MCP server via stdio. Data stays on laptop. Claude Code, Cursor, Windsurf connect via MCP config.                                                Solo dev. Air-gapped. Maximum data sovereignty.

  **B. Remote (V0.3 target)**        OAF on a remote server (VM/container). MCP gateway over HTTPS + SSE. Cloud AI tools (Claude.ai skill, ChatGPT action) connect as MCP clients. Auth via API keys/OAuth.   Cloud AI tools. Team shared workspace. CI/CD integration. Mobile access.

  **C. Hybrid (V1.0 target)**        Local OAF for runtime/container management. Remote OAF for memory persistence. Sync via lightweight replication or Git-backed state.                                     Fast local dev + persistent cloud memory. Multiple devices. Enterprise centralized governance.
  ––––––––––––––––– –––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––– ––––––––––––––––––––––––––––––––––––––––––––––––

## 2.3 Unified Architecture

+–––––––––––––––––––––––––––––––––––-+
**OAF Unified Architecture**
┌─────────────────────────────────────────────────────────────┐
│ CLIENTS: Claude Code Cursor Windsurf Claude.ai ChatGPT │
│ (stdio) (stdio) (stdio) (SSE) (SSE) │
└──────────────────────────────┴──────────────────────────────┘
▼
┌─────────────────────────────────────────────────────────────┐
│ P4: MCP GATEWAY (Auth + Policy + Routing + Audit) │
└─────────────────────────────────────────────────────────────┘
▼ ▼ ▼
┌─────────────────┐ ┌─────────────────┐ ┌─────────────────┐
│ P2: PROJECT │ │ P3: STATE │ │ P1: RUNTIME │
│ MEMORY │ │ INDEX │ │ SHELL │
│ SQLite + FTS5 │ │ Git + JSONL │ │ Docker+Volumes │
└─────────────────┘ └─────────────────┘ └─────────────────┘
▼
┌─────────────────────────────────────────────────────────────┐
│ WORKSPACE: Filesystem + Git + .oaf/ (canonical truth) │
└─────────────────────────────────────────────────────────────┘
+–––––––––––––––––––––––––––––––––––-+

## 2.4 State Model

The filesystem expresses the live project. Git expresses committed lineage. .oaf/ expresses accelerated knowledge. If divergence occurs, OAF reconciles toward filesystem and Git rather than preserving independent opaque state.

  –––––––––– –––––––––– –––––––––––––––––––- ––––––––––––––––––––-
  **Layer**            **Type**             **Role**                                **V1 Rule**

  **Filesystem**       Canonical            Current project content and outputs     Primary source of truth

  **Git**              Canonical            Versioned state and history             Primary reference for lineage

  **.oaf/inventory**   Derived              Fast project state index                Rebuildable. Optimized for fast resume.

  **.oaf/memory**      Derived              Decision records, retrievable context   Consultative only. Never blocks.

  **.oaf/events**      Derived (critical)   Append-only action log                  Required for audit + reconstruction

  **Gateway**          Operational          Controlled execution surface            Mandatory for remote access
  –––––––––– –––––––––– –––––––––––––––––––- ––––––––––––––––––––-

## 2.5 Architecture Invariants

-   **One active writer per workspace:** No concurrent writes. Write token is lease-based with expiration.

-   **Explicit sessions:** A session must be opened before any remote execution is permitted.

-   **Everything evented:** Every stateful action is logged to events.jsonl.

-   **Policy-gated sensitive actions:** File writes, shell execution, secret access, and dependency installation pass through the policy engine.

-   **Reconstructible .oaf/:** Must be rebuildable from filesystem + Git + event history.

-   **Deterministic runtime identity:** Runtime identity hash must detect incompatible reuse.

-   **MCP-native:** All model-facing interactions use standard MCP protocol. No custom protocols.

## 2.6 Security Model

  ––––––––––- –––––––––––––––––– ––––––––––––––––––––––––-
  **Aspect**            **Local Topology**                   **Remote Topology**

  **Transport**         stdio (inherently trusted)           HTTPS + TLS 1.3 only. MCP-over-SSE.

  **Authentication**    None required (local user)           API key (simple) or OAuth 2.0 + PKCE (team)

  **Authorization**     Minimal: write token for writes      Role-based: reader, writer, operator, admin

  **Session leases**    Optional                             Mandatory. Default 30 min TTL. Auto-expire.

  **Secrets**           Whitelist access via named aliases   DENIED by default. Never exposed remotely.

  **Audit**             All events logged                    All events logged + source IP + client identity

  **Shell execution**   Approval-gated                       Denied by default. Unlock via explicit policy.
  ––––––––––- –––––––––––––––––– ––––––––––––––––––––––––-

## 2.7 Technology Stack

  –––––––––––––- –––––––––––––––––––––– –––––––––––––––––––––––––––––––––––––––––
  **Component**               **Recommended**                              **Rationale**

  **CLI binary**              Rust (clap + tokio)                          Fast startup (\<50ms), single binary, cross-platform. Go acceptable alternative.

  **MCP server**              TypeScript (MCP SDK) or Rust (rmcp)          TS has best MCP ecosystem. Rust if unified with CLI.

  **Local storage**           SQLite (rusqlite or better-sqlite3)          Zero config, embedded. FTS5 for text search. WAL mode.

  **Event log**               JSONL files                                  Human-readable, append-only, grep-friendly, reconstructible.

  **Container runtime**       Docker + DevContainers spec                  Industry standard. Works with VS Code, Cursor, JetBrains.

  **Cache persistence**       Named Docker volumes                         Survive container rebuilds. Scoped per project + runtime ID.

  **Policy engine**           YAML config + evaluator                      Declarative, human-readable, versionable. No OPA for V1.

  **Vector search (V0.4+)**   sqlite-vss or Qdrant embedded                Only if FTS5 proves insufficient. Avoid premature complexity.

  **TUI dashboard (V0.3+)**   Ratatui (Rust) or Textual (Python)           Terminal-native, no browser dependency.

  **CI/CD**                   GitHub Actions                               Standard for open-source. Matrix builds.

  **Testing**                 cargo test + vitest. E2E: Docker-in-Docker   Contract tests for MCP. E2E for resume/handoff scenarios.
  –––––––––––––- –––––––––––––––––––––– –––––––––––––––––––––––––––––––––––––––––

# 3. Product Evolution V0.1 – V3.0

Each phase delivers a usable result, validates a distinct hypothesis, introduces minimum new complexity, and has its own marketing narrative.

## 3.1 V0.1 — Foundations

+––––––––––––––––––––––––––––––––––––––––––––––––––––––––––-+
**V0.1 — *\"Never Start From Scratch Again\"***
**Tagline:** Your AI workspace remembers. Resume in seconds, not minutes.
**Hero feature:** oaf resume — one command, workspace is back. Plus MCP memory server any AI tool can connect to.
**Demo:** 30-second video: close laptop, reopen, oaf resume, environment restored. Side-by-side with the old way.
+––––––––––––––––––––––––––––––––––––––––––––––––––––––––––-+

**Goal:** Prove that a workspace can be resumed without restarting the world.

Must Include

-   **Workspace initialization:** oaf init detects project type, generates scaffold, creates runtime manifest.

-   **Deterministic runtime identity:** Hash of devcontainer.json + lockfiles + tool versions.

-   **Inventory refresh:** Fast file index in SQLite. Scoped scanning.

-   **Event log:** Append-only JSONL for every stateful action.

-   **Doctor and repair:** Health checks with structured output. Safe automated fixes.

-   **Runtime persistence:** Named Docker volumes for Python/Node caches. DevContainer template.

-   **MCP memory server (local):** SQLite-backed. Expose write_memory, search_memory, log_decision, get_handoff_summary via stdio MCP.

-   **Client connector:** oaf connect claude-code\|cursor\|windsurf generates MCP config.

-   **CLI-first:** init, resume, doctor, state, connect, repair, test.

Must Avoid

-   No concurrency beyond single active writer.

-   No remote gateway (local MCP only via stdio).

-   No vector search (FTS5 only).

-   No TUI dashboard (CLI output only).

-   No plugin/extension system.

Exit Criteria

-   Users can close a project, return later, run oaf resume, and recover a usable workspace in \<30 seconds.

-   A model connected via MCP can search memory and read handoff summaries.

**Timeline:** 6 weeks.

## 3.2 V0.2 — Sequential Model Handoff

+––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––+
**V0.2 — *\"Switch Models, Keep the Thread\"***
**Tagline:** Work with Claude today, switch to GPT tomorrow. Your project doesn't care which AI you use.
**Hero feature:** Cross-model handoff. Claude Code writes decisions → Cursor reads them. No prompt scaffolding.
**Demo:** Split-screen: Claude Code makes 5 decisions, user switches to Cursor, types "continue the refactoring", Cursor knows exactly what to do.
+––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––+

**Goal:** Prove that one model can resume another model's work without full project rediscovery.

Must Include

-   **Actor and session model:** open/close_session, attach_actor, write token management.

-   **Shared project memory + private session memory:** Project memory is durable and shared. Session memory is private and lower-retention.

-   **Handoff summary generation:** Structured packet with goal, changed files, decisions, risks, next actions.

-   **Context generation:** oaf context produces a compact project onboarding file.

-   **Import/export:** oaf import CLAUDE.md and oaf export claude-md for migration and anti lock-in.

-   **Mini dashboard:** CLI-rendered state: active actor, writer token, runtime identity, recent decisions.

Must Avoid

-   No simultaneous writing.

-   No remote/web model access (unless manually proxied outside OAF).

-   No advanced dependency impact blocker.

Exit Criteria

-   A second model resumes useful work with materially less prompt scaffolding (measurable).

-   Import from CLAUDE.md works. Export back works.

**Timeline:** +4 weeks (week 10).

## 3.3 V0.3 — Controlled Gateway + Remote Access

+––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––+
**V0.3 — *\"Your Workspace, Accessible from Anywhere\"***
**Tagline:** Connect Claude.ai, ChatGPT, or any AI to your project — from the cloud, with guardrails.
**Hero feature:** Remote MCP gateway. Use a Claude skill from your phone → persist decisions → pick up on laptop.
**Demo:** Developer on phone (Claude.ai) makes architecture decisions during commute. At desk: oaf resume — everything is there.
+––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––+

**Goal:** Allow remote or web-hosted models to use the workspace through an explicit, inspectable control surface.

Must Include

-   **MCP gateway service:** Local + SSE/HTTPS transport for remote access. Single binary or daemon.

-   **Authentication:** API key (V0.3). OAuth 2.0 (V0.4+).

-   **Policy engine:** YAML-based rules. Action classes: read, write, execute, secret. Decisions: allow, deny, approve.

-   **Approval hooks:** CLI-based approval prompts with command preview and diff.

-   **Gateway event tracing:** Every tool call logged with full provenance.

-   **Multi-project support:** oaf_set_project for remote topology.

-   **Deployment template:** Dockerfile + docker-compose for remote OAF server. Reference Fly.io config.

Must Avoid

-   No cloud-initiated direct machine ingress (gateway mediates everything).

-   No permanently open remote session (leases with expiration).

-   No unrestricted shell for remote clients (denied by default).

Exit Criteria

-   A remote model (Claude.ai) can write decisions and read handoff summaries via HTTPS.

-   Every remote action is audited and policy-gated.

**Timeline:** +6 weeks (week 16).

## 3.4 V0.4 — Memory & Recovery Hardening

**Goal:** Make memory and reconstruction genuinely useful rather than merely present.

Must Include

-   **Memory status model:** hypothesis → validated → obsolete → rejected. Promotion flows with audit.

-   **Crash recovery:** Stale session cleanup, write token expiration, forced reclamation.

-   **State rebuild:** Reconstruct .oaf/ from filesystem + Git + event history. Tolerate partial loss.

-   **Dependency mapping:** Language-specific adapters for import/dependency impact. Graceful degradation.

-   **OAuth support:** For remote topology. PKCE flow.

-   **Rate limiting:** Per-client configurable limits for remote access.

Exit Criteria

-   Recovery is trusted: corrupted .oaf/ can be rebuilt. Memory helps more often than it misleads.

**Timeline:** +6 weeks (week 22).

## 3.5 V1.0 — Stable Technical Substrate

+–––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––+
**V1.0 — *\"The Workspace Standard\"***
**Tagline:** The open standard for AI-assisted workspaces. Persistent. Inspectable. Transferable. Governed.
**Hero feature:** Stable contracts, reference demos, compatibility matrix, contributor docs. The substrate is ready.
**Demo:** Third party installs OAF, connects Claude Code, and is productive in 5 minutes with zero guidance.
**Marketing shift:** From "tool" to "standard." Position OAF as what MCP is for tool interop, but for workspace persistence.
+–––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––+

Must Include

-   **Stable CLI and gateway contract:** Frozen MCP tool surface. Contract tests.

-   **Architecture and threat model docs:** Published, reviewed, contributor-accessible.

-   **Compatibility matrix:** Tested: Linux, macOS, Windows. Claude Code, Cursor, Windsurf.

-   **Hybrid topology:** Local-remote sync protocol.

-   **Reference demos:** Python project, Node/TS project. Resume, handoff, gateway scenarios.

-   **Benchmarks:** Published resume latency, handoff quality, rebuild time.

-   **Claude.ai skill template:** Ready-to-deploy MCP config for Claude.ai.

Exit Criteria

-   Third parties can install, evaluate, contribute, and report issues with minimal guidance.

**Timeline:** +4 weeks (week 26 / month 6).

## 3.6 V2.0 — Parallel Work Streams

+––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––-+
**V2.0 — *\"The Forge Ignites\"***
**Tagline:** Multiple AI agents, one project, zero chaos. The Forge is open.
**Hero feature:** Parallel agent tracks via Git worktrees. Agent A codes, Agent B reviews, Agent C documents.
**Demo:** 3-panel screen: Builder agent writes feature, Reviewer agent catches bug, Documentation agent updates README. All on one project.
**Name payoff:** THIS is when "Omni-Agent Forge" earns its name. The forge where agents are shaped and coordinated.
+––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––-+

Must Include

-   **Worktree-backed execution tracks:** Git worktrees as default parallelism unit.

-   **Role split:** Writer, reviewer, auditor roles with capability constraints.

-   **Cross-track diff and merge:** Test-gated merges with origin traceability.

-   **Team RBAC:** Per-user/per-model permissions on remote topology.

Exit Criteria

-   Parallel AI work is demonstrably safe because isolated and reviewable, not because uncontrolled.

**Timeline:** +12 weeks (month 9).

## 3.7 V3.0 — Coordinated Actor Ecosystem

+–––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––-+
**V3.0 — *\"Orchestrated Intelligence\"***
**Tagline:** Specialized AI roles. Policy-driven routing. Compound workflows. The OS for AI-assisted engineering.
**Hero feature:** Role-based actors (builder, reviewer, auditor, release operator) with policy templates and observable task graphs.
**Demo:** Full release workflow: planning agent → builder agents → reviewer agent → release operator agent. All governed, all traced.
+–––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––-+

Must Include

-   **Specialized actor roles:** Builder, reviewer, auditor, release operator with inherited capability sets.

-   **Policy-driven routing:** Tasks routed to best-suited actor based on capability profile.

-   **Compound workflows:** Explicit task graphs across build, docs, review, and release.

-   **Richer governance:** Observability dashboards. Audit export. Enterprise SSO.

-   **Managed SaaS option:** oaf.dev hosted service. Free tier + team plans.

Must Avoid

-   No hidden autonomous system that bypasses approvals.

-   No assumption that more actors always improve outcomes.

-   Benchmark every orchestration claim against simpler sequential baseline.

# 4. Detailed Function & Skill Catalog

44 functions organized by subsystem. Each entry includes: role, phase, implementation guidance, exposure model, and dependencies.

## 4.1 Workspace & Runtime

+–––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––+
**init_workspace()** — Phase 0.1
**Role:** Create .oaf/ scaffold, manifests, base config, detect project type, generate devcontainer.json if absent
**Implementation:** CLI command. Detect Python (pyproject.toml, requirements.txt), Node (package.json), Rust (Cargo.toml), Go (go.mod). Generate .oaf/runtime.json manifest. Create .oaf/memory.db (SQLite). Initialize events.jsonl. Template devcontainer.json with cache volumes.
**Exposure:** Internal (CLI) **\| Dependencies:** None
+–––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––+

+––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––+
**detect_runtime_identity()** — Phase 0.1
**Role:** Compute deterministic hash from project type, branch, lockfile hashes, base image, language versions
**Implementation:** Pure function. SHA-256 over: devcontainer.json + lockfile(s) + .tool-versions + .nvmrc. Store in .oaf/runtime.json. Contract-test heavily for determinism.
**Exposure:** Internal **\| Dependencies:** None
+––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––+

+–––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––-+
**snapshot_runtime()** — Phase 0.1
**Role:** Capture restorable runtime state: cache references, installed extras, lockfile state, image metadata
**Implementation:** Serialize current state to .oaf/snapshot.json. Record Docker volume names, mounted paths, language version outputs. Used by restore_env() for comparison.
**Exposure:** Internal **\| Dependencies:** Docker API (optional)
+–––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––-+

+––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––+
**restore_env()** — Phase 0.1
**Role:** Recreate or refresh runtime from manifests and persisted caches. Emit structured diff on mismatch.
**Implementation:** Compare snapshot.json vs live environment. Restore named Docker volumes. Run lockfile install if drift detected. Emit JSON diff report. Prefer controlled replay over opaque binary reuse.
**Exposure:** Internal (called by oaf resume) **\| Dependencies:** snapshot_runtime()
+––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––+

+–––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––+
**doctor_check()** — Phase 0.1
**Role:** Run environment, dependency, and workspace health checks. Machine-readable + human summary.
**Implementation:** Bundle checks: runtime identity match, lockfile consistency, .oaf/ integrity, Docker health, Git status, disk space. Output JSON + colored CLI summary. Exit code reflects severity.
**Exposure:** Model-exposed (read-only) **\| Dependencies:** detect_runtime_identity()
+–––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––+

+––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––-+
**repair_workspace()** — Phase 0.1
**Role:** Apply safe automated fixes for known health issues. Approval on destructive operations.
**Implementation:** Fix catalog: rebuild .oaf/ from Git + events, reinstall deps from lockfiles, reclaim stale sessions, prune orphan volumes. Each fix tagged safe/destructive. Destructive requires \–force or interactive approval.
**Exposure:** Internal (CLI) **\| Dependencies:** doctor_check()
+––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––-+

+–––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––+
**run_isolated_test()** — Phase 0.1
**Role:** Run project tests in controlled workspace runtime. Capture structured results.
**Implementation:** Detect test runner (pytest, vitest, cargo test, go test). Run inside container. Capture: exit code, stdout/stderr, duration, test count, failures. Store result in events.jsonl.
**Exposure:** Model-exposed (V0.3+) **\| Dependencies:** restore_env()
+–––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––+

+––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––+
**build_artifact()** — Phase 0.2
**Role:** Build project deliverables (binaries, docs, packages) under controlled runtime.
**Implementation:** Detect build system. Execute build command. Capture outputs, durations, warnings. Log to events. Unify code and document build workflows under one action.
**Exposure:** Model-exposed (V0.3+) **\| Dependencies:** restore_env()
+––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––+

## 4.2 Inventory & State

+––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––-+
**refresh_inventory()** — Phase 0.1
**Role:** Update physical state index: files, services, ports, manifests. Scoped scanning.
**Implementation:** Walk filesystem with gitignore-aware filter. Store in SQLite .oaf/inventory.db: path, size, mtime, language, hash (optional). Incremental update based on mtime. Avoid full rescan unless \–force.
**Exposure:** Internal (called by oaf resume) **\| Dependencies:** None
+––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––-+

+––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––-+
**list_workspace_state()** — Phase 0.1
**Role:** Return concise operational snapshot: file counts, runtime identity, active sessions, recent events, health.
**Implementation:** Query inventory.db + runtime.json + events.jsonl tail + session table. Return JSON object. Drive CLI status command and mini dashboard.
**Exposure:** Model-exposed (read-only) **\| Dependencies:** refresh_inventory()
+––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––-+

+–––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––-+
**scan_services()** — Phase 0.3
**Role:** Detect local services relevant to workspace: containers, ports, databases, named processes.
**Implementation:** Docker ps + port scan + process name matching. Optional adapters per stack (PostgreSQL, Redis, etc). Graceful degradation when services not detected.
**Exposure:** Model-exposed (V0.3+) **\| Dependencies:** Docker API
+–––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––-+

+––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––+
**diff_workspace_state()** — Phase 0.2
**Role:** Show what changed since previous state baseline or since a specific event/timestamp.
**Implementation:** Compare current inventory vs stored baseline. Use git diff for tracked files. Overlay .oaf/ event log for untracked state changes. Output: added/modified/deleted files, decision changes, session events.
**Exposure:** Model-exposed (read-only) **\| Dependencies:** refresh_inventory()
+––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––+

+––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––-+
**rebuild_state()** — Phase 0.4
**Role:** Reconstruct derived state (.oaf/) from repo, manifests, and event history. Tolerate partial loss.
**Implementation:** Delete and regenerate inventory.db from filesystem. Replay events.jsonl to rebuild memory indices. Validate against Git history. Report unrecoverable gaps. Must tolerate: missing .oaf/memory.db, corrupt events, stale snapshots.
**Exposure:** Internal (CLI) **\| Dependencies:** All state functions
+––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––-+

## 4.3 Memory & Handoff

+––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––-+
**write_memory_entry()** — Phase 0.2
**Role:** Store a structured project or session memory record with type, status, and provenance.
**Implementation:** Insert into SQLite memory.db. Schema: id (ULID), type (decision\|artifact\|goal\|risk\|note\|observation), status (hypothesis\|validated\|obsolete\|rejected), content (text), actor, session_id, timestamp, linked_files (JSON array), linked_commits (JSON array), tags (JSON array). FTS5 index on content+tags.
**Exposure:** Model-exposed (MCP tool) **\| Dependencies:** SQLite + FTS5
+––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––-+

+–––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––-+
**search_memory()** — Phase 0.2
**Role:** Retrieve relevant decisions, notes, artifacts by query. Full-text + metadata filters.
**Implementation:** SQLite FTS5 MATCH query. Filters: type, status, actor, date range, linked_file. Return ranked results with snippets. Phase 2 (V0.4+): optional sqlite-vss vector similarity if FTS5 proves insufficient. Hybrid: FTS5 first, vector as re-ranker.
**Exposure:** Model-exposed (MCP tool) **\| Dependencies:** write_memory_entry()
+–––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––-+

+–––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––-+
**log_decision()** — Phase 0.2
**Role:** Write a decision record with rationale, status, references. Convenience wrapper over write_memory_entry.
**Implementation:** Specialized write_memory_entry with type=decision. Additional fields: rationale (text), alternatives_considered (JSON), impact_areas (JSON), reversibility (enum: easy\|moderate\|hard\|irreversible). Auto-link to current session and recent files.
**Exposure:** Model-exposed (MCP tool) **\| Dependencies:** write_memory_entry()
+–––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––-+

+–––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––+
**promote_decision_status()** — Phase 0.4
**Role:** Transition decision trust state: hypothesis → validated → obsolete. Audit trail.
**Implementation:** Update status field with: previous_status, promoted_by (actor), promoted_at, promotion_reason. Append promotion event to events.jsonl. Validate allowed transitions (no direct hypothesis→obsolete).
**Exposure:** Model-exposed (MCP tool) **\| Dependencies:** log_decision()
+–––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––+

+–––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––-+
**invalidate_memory_entry()** — Phase 0.4
**Role:** Retire stale or incorrect memory. Never silent delete — status change + reason.
**Implementation:** Set status=rejected or status=obsolete. Record: invalidated_by, reason, replacement_id (optional link to corrected entry). Entry remains searchable with status filter. Soft-delete only.
**Exposure:** Model-exposed (MCP tool) **\| Dependencies:** write_memory_entry()
+–––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––-+

+–––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––+
**get_handoff_summary()** — Phase 0.2
**Role:** Produce structured transfer packet for another actor/model to resume work.
**Implementation:** Aggregate: current_goal (from latest goal-type memory), recent_decisions (last N decisions, sorted by recency), changed_files (from git diff since session start), open_risks (status=hypothesis, type=risk), unresolved_questions, recommended_next_actions, tech_stack_summary. Return as JSON. Configurable depth (compact/full).
**Exposure:** Model-exposed (MCP tool) **\| Dependencies:** search_memory(), diff_workspace_state()
+–––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––+

## 4.4 Sessions & Actors

+––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––-+
**open_session()** — Phase 0.2
**Role:** Start a bounded actor session with identity, permissions scope, and lease duration.
**Implementation:** Insert into sessions table: session_id (ULID), actor_id, actor_type (human\|model\|ci), model_name (optional), started_at, lease_duration, permissions_scope, status (active\|closed\|expired). Emit session_opened event. Auto-expire after lease.
**Exposure:** Model-exposed (MCP tool, auto-called) **\| Dependencies:** None
+––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––-+

+––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––+
**close_session()** — Phase 0.2
**Role:** End session cleanly. Emit summary event. Release write token if held.
**Implementation:** Update session status=closed, ended_at=now(). Generate session_summary: duration, events_count, decisions_made, files_changed. Release write token. Emit session_closed event.
**Exposure:** Model-exposed (MCP tool) **\| Dependencies:** open_session()
+––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––+

+–––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––+
**attach_actor()** — Phase 0.2
**Role:** Associate a model or user identity with a session. Capture capability profile.
**Implementation:** Record: actor_id, actor_type, model_name, model_version, capability_tags (e.g., code, docs, review), preferred_role. Stored in session metadata. Used by policy engine to scope permissions.
**Exposure:** Internal (auto on session open) **\| Dependencies:** open_session()
+–––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––+

+–––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––+
**acquire_write_token()** — Phase 0.2
**Role:** Grant exclusive write authority to one active actor. Lease-based, not lock-based.
**Implementation:** Check: no other active write token. If free: grant token with lease_duration (default 15min, renewable). Store in .oaf/write_token.json: holder_session, granted_at, expires_at. Refuse if held by another. Emit write_token_acquired event.
**Exposure:** Model-exposed (MCP tool) **\| Dependencies:** open_session()
+–––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––+

+–––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––+
**release_write_token()** — Phase 0.2
**Role:** Release or expire active write authority. Support forced reclamation.
**Implementation:** Clear write_token.json. If expired: auto-release with warning event. If forced (\–force): require operator confirmation, emit forced_reclaim event with justification. Stale sessions auto-cleaned.
**Exposure:** Model-exposed (MCP tool) **\| Dependencies:** acquire_write_token()
+–––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––+

+–––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––+
**create_worktree()** — Phase 2.0
**Role:** Create isolated execution track for parallel work via Git worktree.
**Implementation:** git worktree add .oaf/worktrees/\<name\> -b \<branch\>. Copy .oaf/ metadata (memory.db is shared, session table is scoped). Each worktree gets its own runtime identity and snapshot. Attach actor/session metadata to worktree.
**Exposure:** Model-exposed (V2.0+) **\| Dependencies:** Git, open_session()
+–––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––+

+–––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––-+
**merge_worktree()** — Phase 2.0
**Role:** Merge a parallel track back with tests and traceability.
**Implementation:** Pre-merge: run tests in worktree, generate diff summary, check policy gates. Merge via git merge with \–no-ff. Post-merge: update inventory, log merge event with origin actor/session/worktree. Remove worktree. Fail-safe: never auto-merge if tests fail.
**Exposure:** Model-exposed (V2.0+) **\| Dependencies:** create_worktree(), run_isolated_test()
+–––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––-+

## 4.5 Gateway & Policy

+––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––+
**start_gateway()** — Phase 0.3
**Role:** Start local MCP gateway service. Expose tool surface to local or remote clients.
**Implementation:** Start MCP server. Two transports: stdio (local, default), SSE over HTTPS (remote, opt-in). Load policies from .oaf/policies/\*.yaml. Open listener. Log gateway_started event. Auto-stop on inactivity timeout (configurable).
**Exposure:** Internal (CLI: oaf gateway start) **\| Dependencies:** Policy files
+––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––+

+––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––+
**stop_gateway()** — Phase 0.3
**Role:** Stop gateway and revoke all remote execution capability. Close all active sessions.
**Implementation:** Close all active sessions (emit close events). Release all write tokens. Stop listener. Log gateway_stopped event. No hidden always-on service by default.
**Exposure:** Internal (CLI: oaf gateway stop) **\| Dependencies:** start_gateway()
+––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––+

+–––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––+
**attach_remote_model()** — Phase 0.3
**Role:** Bind a remote model session to the workspace via gateway. Requires explicit action.
**Implementation:** Authenticate client (API key or OAuth token). Open session with remote scope. Assign permissions based on role (reader/writer/operator). Log remote_model_attached event with: client_ip, model_identity, granted_scope.
**Exposure:** Auto (on MCP connection) **\| Dependencies:** start_gateway(), open_session()
+–––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––+

+––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––+
**policy_check()** — Phase 0.3
**Role:** Evaluate whether an action is allowed, denied, or requires approval. Central authorization.
**Implementation:** Input: action_class, actor, session, parameters. Load matching policy rule from .oaf/policies/. Evaluate conditions (actor_type, scope, file_path patterns, command whitelist). Return: {decision: allow\|deny\|approve, rule_id, reason}. Log policy_evaluated event.
**Exposure:** Internal (called by gateway) **\| Dependencies:** Policy YAML files
+––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––+

+––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––-+
**request_approval()** — Phase 0.3
**Role:** Prompt user for approval with context: command, diff, reason, risk level.
**Implementation:** Display in CLI: action description, affected files/commands, risk level, timeout. For TUI: render in dashboard panel. For remote: webhook or push notification (V1.0+). Capture: approved/denied, approver, timestamp. Log approval_decision event.
**Exposure:** Internal (triggered by policy_check) **\| Dependencies:** policy_check()
+––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––-+

+––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––-+
**execute_tool_call()** — Phase 0.3
**Role:** Dispatch a tool action from model to workspace. Wrap with eventing and policy.
**Implementation:** Pipeline: receive MCP tool call → policy_check() → if approve: request_approval() → if allowed: dispatch to OAF core function → capture result → log tool_call_executed event with full trace. Timeout per call (configurable). Sandbox shell commands.
**Exposure:** Internal (gateway orchestrator) **\| Dependencies:** policy_check(), all core functions
+––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––-+

+–––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––+
**read_secret()** — Phase 0.3
**Role:** Access controlled secret values. Whitelist-only. Named aliases, never raw paths.
**Implementation:** Secrets defined in .oaf/policies/secrets.yaml as named aliases mapping to: env var, OS keychain entry, or .env file key. Never expose raw value in MCP response for remote clients. Local clients: return value. Remote clients: DENIED by default. Log secret_access event.
**Exposure:** Model-exposed (local only by default) **\| Dependencies:** policy_check()
+–––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––+

+–––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––+
**install_dependency()** — Phase 0.3
**Role:** Install a dependency through controlled runtime pathway. Never arbitrary package manager use.
**Implementation:** Validate: package name against allowlist (if configured), or require approval. Execute install via appropriate package manager inside container. Update lockfile. Log dependency_installed event with: package, version, installer, policy_decision. Snapshot runtime after.
**Exposure:** Model-exposed (approval-gated) **\| Dependencies:** policy_check(), snapshot_runtime()
+–––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––+

## 4.6 Observability

+–––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––-+
**tail_events()** — Phase 0.1
**Role:** Read recent event activity for operators, dashboards, and debugging.
**Implementation:** Read last N lines of events.jsonl. Parse and filter by: event_type, actor, session, time_range. Output as JSON array or formatted CLI table. Support \–follow mode (tail -f equivalent).
**Exposure:** Model-exposed (read-only) **\| Dependencies:** events.jsonl
+–––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––-+

+––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––+
**export_context_bundle()** — Phase 0.4
**Role:** Package state, logs, summaries for support, debugging, or external handoff.
**Implementation:** Generate ZIP containing: runtime.json, recent events (last 100), memory dump (decisions only), inventory summary, session history, doctor_check output, git log \–oneline -20. Redact secrets. Useful for bug reports and offline review.
**Exposure:** Internal (CLI: oaf export-bundle) **\| Dependencies:** All state functions
+––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––+

+–––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––+
**package_release_notes()** — Phase 1.0
**Role:** Produce release notes from milestones, changelog fragments, and decision records.
**Implementation:** Aggregate: Git commits since last tag, decisions with status=validated, closed sessions with summaries, test results. Template output as markdown. Distinguish: features, fixes, breaking changes, experimental, deprecated.
**Exposure:** Internal (CLI: oaf release-notes) **\| Dependencies:** search_memory(), Git
+–––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––+

+–––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––-+
**benchmark_resume()** — Phase 1.0
**Role:** Measure and report resume latency, handoff quality, rebuild time. Repeatable.
**Implementation:** Automated benchmark suite: cold start time, oaf resume time, handoff summary generation time, rebuild time, memory search latency (p50/p95/p99). Output JSON report. Publish as CI artifact. Used to validate product claims.
**Exposure:** Internal (CLI: oaf benchmark) **\| Dependencies:** All core functions
+–––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––-+

## 4.7 New

+––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––+
**oaf_connect(client)** — Phase 0.1
**Role:** Generate MCP configuration for a specific client. Write to client config file. Zero-friction onboarding.
**Implementation:** Supported clients: claude-code, cursor, windsurf, vscode. Detect client config path (\~/.claude/settings.json, .cursor/mcp.json, etc). Generate MCP server entry with: transport (stdio for local, SSE for remote), command/args, env vars. For remote: prompt for server URL and API key.
**Exposure:** Internal (CLI: oaf connect claude-code) **\| Dependencies:** None
+––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––+

+––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––+
**oaf_context()** — Phase 0.2
**Role:** Generate compact context file (.oaf/context.md) consumable by any model. Project onboarding in one read.
**Implementation:** Aggregate: project name, tech stack, directory structure (depth 2), recent decisions (last 10), active goals, known risks, conventions, build/test commands, team/actor history. Output as structured markdown. Replaces per-tool instruction files (CLAUDE.md, .cursorrules).
**Exposure:** Model-exposed (MCP tool) **\| Dependencies:** search_memory(), list_workspace_state()
+––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––+

+–––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––-+
**oaf_import(source)** — Phase 0.2
**Role:** Import existing CLAUDE.md, .cursorrules, or AGENTS.md into OAF memory. Migration path.
**Implementation:** Parse source file. Extract: instructions → type=note, decisions → type=decision, conventions → type=observation. Insert into memory.db with status=validated (imported content is trusted). Log import event.
**Exposure:** Internal (CLI: oaf import CLAUDE.md) **\| Dependencies:** write_memory_entry()
+–––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––-+

+––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––+
**oaf_export(target)** — Phase 0.2
**Role:** Export OAF memory as CLAUDE.md, .cursorrules, or generic markdown. Anti lock-in.
**Implementation:** Query memory.db for validated decisions, notes, conventions. Template into target format. For CLAUDE.md: generate structured markdown with sections. For .cursorrules: JSON format. Ensures OAF is reversible.
**Exposure:** Internal (CLI: oaf export claude-md) **\| Dependencies:** search_memory()
+––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––+

+––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––-+
**oaf_set_project(id)** — Phase 0.3
**Role:** Switch active project context on a multi-project OAF instance. Remote topology.
**Implementation:** Set active project_id in session context. All subsequent MCP tool calls scoped to this project. Validate project exists. Log project_switched event. For remote: project scoping via API key or explicit tool call.
**Exposure:** Model-exposed (MCP tool) **\| Dependencies:** open_session()
+––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––-+

+–––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––+
**oaf_benchmark()** — Phase 1.0
**Role:** Run full benchmark suite and produce publishable report.
**Implementation:** Wrapper around benchmark_resume() + additional checks: handoff quality score (measure context preservation across model switch), memory search relevance, policy evaluation latency. Output: JSON + markdown report.
**Exposure:** Internal (CLI: oaf benchmark) **\| Dependencies:** benchmark_resume()
+–––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––+

## 4.8 Skill Exposure Matrix

Which functions are exposed to AI models at each phase.

  ––––––––––– ––––––––––––––––––––––––––––––––––––––––––––––––––––––––– ––––––––––––––––––––––––––––
  **Phase**              **Expose to Models**                                                                                               **Keep Internal / Operator**

  **0.1**                doctor_check, list_workspace_state, run_isolated_test, tail_events                                                 init, snapshot, restore, repair, refresh_inventory

  **0.2**                \+ write/search_memory, log_decision, get_handoff_summary, oaf_context, open/close_session, diff_workspace_state   Write token management, import/export

  **0.3**                \+ Most gateway tools under policy: read_file, write_file, list_files, install_dependency (approval-gated)         Secret handling internals, repair plans, policy config

  **0.4+**               \+ promote_decision_status, invalidate_memory, export_context_bundle                                               Low-level state surgery, rebuild internals

  **2.0+**               \+ create/merge_worktree                                                                                           Worktree lifecycle internals
  ––––––––––– ––––––––––––––––––––––––––––––––––––––––––––––––––––––––– ––––––––––––––––––––––––––––

# 5. Repository Structure & Contributor Guide

## 5.1 Repository Layout

oaf/

README.md \# 30-second pitch + quick start

LICENSE \# MIT or Apache-2.0

CHANGELOG.md \# User-facing change history

CONTRIBUTING.md \# Setup, conventions, PR process

SECURITY.md \# Vulnerability reporting

GOVERNANCE.md \# Decision process, RFC/ADR rules

ROADMAP.md \# Now / Next / Later / Not Planned

CODE_OF_CONDUCT.md

docs/

product-charter.md \# Mission, scope, non-goals, principles

architecture.md \# System model, pillars, invariants

runtime-model.md \# Runtime identity, persistence, rebuild

memory-model.md \# Memory classes, statuses, retention

security-model.md \# Threat model, policies, approvals

gateway-model.md \# MCP gateway, remote access, auth

testing-strategy.md \# How the product is tested

release-policy.md \# Versioning and release discipline

compatibility-matrix.md \# OS, tools, language versions

deployment-guide.md \# Local, remote, hybrid setup

rfcs/ \# Proposals for significant changes

adrs/ \# Architectural Decision Records

src/oaf/ \# Core source code

cli/ \# CLI commands (init, resume, doctor\...)

mcp/ \# MCP server implementation

memory/ \# SQLite memory layer

state/ \# Inventory, events, state index

gateway/ \# Policy engine, auth, gateway service

runtime/ \# Container lifecycle, identity

tests/

unit/ \# Fast, isolated tests

integration/ \# Subsystem interaction tests

e2e/ \# Full scenario tests

contract/ \# MCP tool surface contracts

benchmark/ \# Performance measurements

fixtures/ \# Test data and scenarios

scripts/

dev/ \# Developer utilities

release/ \# Release automation

benchmark/ \# Benchmark runners

templates/

devcontainer/ \# Reference DevContainer configs

policies/ \# Default policy files

mcp-configs/ \# Client MCP config templates

deploy/

docker/ \# Dockerfile for remote OAF server

fly-io/ \# Fly.io deployment config

docker-compose.yaml \# Local + remote compose setup

## 5.2 Documentation Pack

  ––––––––––––––– –––––––––––––––––––––––––––––––––––––––- –––––––––––––––––––––––––––––
  **File**                       **Purpose**                                                                     **Why It Matters Early**

  **README.md**                  High-level entry point. 30-second pitch. Quick start. Why-not-just-use-X FAQ.   Controls first impression. Determines star/bounce ratio.

  **docs/product-charter.md**    Mission, scope, non-goals, principles.                                          Stops scope drift before it starts.

  **docs/architecture.md**       System model, components, invariants.                                           Aligns all implementation debates.

  **docs/security-model.md**     Threat model, policies, approval flows.                                         Makes remote execution defensible.

  **docs/testing-strategy.md**   How the product is tested. What a green suite proves.                           Turns product claims into repeatable checks.

  **ROADMAP.md**                 Now / Next / Later / Not Planned.                                               Makes prioritization visible and protects scope.

  **CONTRIBUTING.md**            Local setup, conventions, PR process, review expectations.                      Improves contribution quality from day one.

  **GOVERNANCE.md**              Decision process, RFC/ADR rules, maintainer roles.                              Prevents chaos as the project grows.
  ––––––––––––––– –––––––––––––––––––––––––––––––––––––––- –––––––––––––––––––––––––––––

## 5.3 RFC & ADR Process

**RFCs required for:** Changes to runtime identity computation, memory schema, gateway semantics, policy model, public MCP tool contracts, and security model.

**ADRs record:** Core architectural decisions that contributors must not quietly bypass. Template: context, decision, consequences, status.

**First ADRs needed:** ADR-001: CLI language (Rust vs TS). ADR-002: MCP-first gateway. ADR-003: SQLite for memory. ADR-004: DevContainers for runtime. ADR-005: JSONL for events.

## 5.4 Versioning & Release

-   **Semantic versioning from day one:** Even during 0.x. Pre-release: 0.1.0-alpha.1, 0.1.0-beta.1, 0.1.0-rc.1.

-   **Trunk-based development:** Short-lived feature branches. Protected main. Release branches for stabilization only.

-   **Release flow:** Scope freeze → stabilization → release candidate → public release → post-release review.

-   **Changelog:** Required for every user-visible change. Distinguish: features, fixes, breaking, experimental, deprecated.

## 5.5 CI/CD Pipeline

  ––––––––––––– ––––––––––––– ––––––––––––––––––––––––
  **Job**                    **When**                   **Purpose**

  **Lint + format**          Every PR                   Code and doc consistency. Fail fast.

  **Unit tests**             Every PR                   Verify isolated logic. Must be \<60s.

  **Integration tests**      Every PR                   Verify subsystem behavior with fixtures.

  **E2E smoke**              Every PR + release         Core scenarios: init, resume, handoff.

  **Contract tests**         Every PR                   MCP tool surface stability.

  **Nightly heavy E2E**      Scheduled                  Crash recovery, remote gateway, long sessions.

  **Benchmark**              Release                    Resume latency, handoff quality, rebuild time.

  **Release verification**   Tag pipeline               Install, upgrade, smoke on clean machine.

  **Docs checks**            Every PR                   Link validation, required file checks.
  ––––––––––––– ––––––––––––– ––––––––––––––––––––––––

## 5.6 Testing Strategy

OAF must test both implementation correctness and product claims. A green unit suite alone does not prove that resume, handoff, or recovery actually work.

-   **Unit:** Manifests, policy checks, decision schemas, session logic, runtime identity computation.

-   **Integration:** Init, inventory refresh, runtime restore, doctor/repair, gateway policy flows.

-   **E2E:** Same-actor resume, cross-model handoff, crash recovery, controlled remote execution.

-   **Contract:** Every public CLI command and MCP tool call has a contract test.

-   **Benchmark:** Resume latency, rebuild latency, handoff payload quality, repair success rates.

-   **Compatibility:** Linux, macOS, Windows. Docker Desktop and Podman.

# 6. Risks, Anti-Patterns & Mitigations

## 6.1 Risk Matrix

  –––––––––––––––– ––––––– ––––––––––––––––––––––––––––––––––––––– ––––––––––––––––––––––––––––––––––––––––––––––––––––
  **Risk**                         **Severity**   **Impact**                                                                     **Mitigation**

  **Vendor absorption**            Critical       Anthropic/GitHub/OpenAI build native workspace persistence within 12 months.   Move fast. V0.1 in 6 weeks. Position as cross-vendor neutral layer. If absorbed: mission accomplished.

  **Scope inflation**              Critical       Feature creep prevents V0.1 from shipping.                                     Hard phase gates. Public Not Planned list. Single maintainer authority for V0.x scope.

  **MCP protocol drift**           High           MCP spec evolves and breaks gateway.                                           Use official MCP SDK. Contribute to spec. Keep gateway surface minimal and versioned.

  **False confidence in memory**   High           AI-written notes become trusted folklore.                                      Status model (hypothesis/validated). Human promotion. Consultative semantics only in V1.

  **Security overreach**           High           Remote-to-local execution exploited for data exfiltration.                     Default-deny. Session leases. Mandatory approval for shell/secrets. Audit trail.

  **State corruption**             Medium         Derived state drifts from repository reality.                                  Rebuild commands. Canonical filesystem/Git rules. Event replay.

  **Docker dependency**            Medium         Some developers resist Docker. Reduces adoption.                               Docker recommended not required. Native mode with degraded capabilities.

  **Premature concurrency**        Medium         Shared-directory multi-writer attempted too early.                             Delay until V2.0 worktree isolation. Sequential-only until proven.

  **Contributor fragmentation**    Low            Too many PRs in too many directions.                                           RFC process for significant changes. ADRs for invariants. Clear CONTRIBUTING.md.
  –––––––––––––––– ––––––– ––––––––––––––––––––––––––––––––––––––– ––––––––––––––––––––––––––––––––––––––––––––––––––––

## 6.2 Anti-Patterns to Explicitly Avoid

+––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––+
⚠ **\"AI Operating System\" inflation**
Claiming OAF is an AI OS or autonomous platform before V2. This invites unfavorable comparison with LangGraph/CrewAI. V0.x is a workspace substrate, not an orchestration framework. Use precise language.
+––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––+

+–––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––-+
⚠ **Opaque background automation**
Running hidden agents or background processes the user didn't ask for. Every action must be explicit, evented, and inspectable. Hidden complexity is acceptable. Hidden authority is not.
+–––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––-+

+–––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––-+
⚠ **Memory-as-truth**
Treating .oaf/memory as the source of truth instead of filesystem + Git. Memory is consultative. It accelerates and explains. It never overrides canonical state.
+–––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––-+

+–––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––-+
⚠ **Unrestricted remote shell**
Allowing remote models to execute arbitrary commands by default. Shell execution for remote clients is DENIED by default. Unlock requires explicit policy rule and approval flow.
+–––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––-+

+––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––-+
⚠ **Multi-writer on shared directory**
Allowing concurrent file edits by multiple agents without isolation. Deceptively hard. Only safe with worktree isolation (V2.0). Never on shared directory.
+––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––-+

+–––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––-+
⚠ **Plugin sprawl before stable core**
Building an extension/plugin system before the core contracts are frozen. Extensions invite scope creep. Freeze core at V1.0 first. Extensions at V1.5+ earliest.
+–––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––-+

+–––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––-+
⚠ **Vanity metrics in benchmarks**
Publishing benchmarks that measure the wrong things (e.g., lines of code generated instead of workspace resume time or handoff quality). Benchmark what matters to the product claim.
+–––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––-+

# 7. Brand, Communication & Community

## 7.1 Narrative Arc: FORGE → OMNI → AGENT

The name Omni-Agent Forge tells a progressive story. Each phase unlocks a keyword:

  –––––––- ––––––- ––––––––––––––––––––––––––––––––––––- ––––––––––––––––––––––––––––––––––––––––––-
  **Phase**       **Keyword**   **Story**                                                                 **Marketing Focus**

  **V0.1–0.2**   **FORGE**     The forge: where your workspace is forged, persisted, and made durable.   Solo devs, early adopters. "Star the repo. Try oaf init. Tell us your resume time."

  **V0.3–1.0**   **OMNI**      Omni: accessible from anywhere. Any model, any client, local or remote.   Teams, power users. "Connect Claude.ai to your project memory."

  **V2.0–3.0**   **AGENT**     Multi-agent: multiple AI agents, coordinated, governed, productive.       Engineering teams. "Orchestrate your AI team. Builder, reviewer, auditor."
  –––––––- ––––––- ––––––––––––––––––––––––––––––––––––- ––––––––––––––––––––––––––––––––––––––––––-

## 7.2 Logo Concepts

Three directions to brief a designer or generate with AI image tools:

+–––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––+
**Concept A: The Anvil Node**
A minimalist anvil shape formed by connected nodes/graph edges. Symbolizes: forging (anvil) + connectivity (nodes) + structure (graph). The anvil's flat surface has a subtle circuit-board pattern. Color palette: deep navy (#1B4F72) + electric blue (#2E86C1) + white. Style: geometric, tech-forward, works at 16px favicon size. Think: the intersection of craftsmanship and computation.
+–––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––+

+––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––-+
**Concept B: The Persistent Flame**
An abstract flame or spark shape that is also a stylized "O" (for Omni) or an infinity symbol. The flame represents the forge. Its persistence represents the core value prop. The dual nature (flame + letter) creates visual intrigue. Color palette: warm forge orange (#E67E22) fading to deep blue (#1B4F72). Style: fluid, modern, single continuous line. Think: energy that never goes out.
+––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––-+

+––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––-+
**Concept C: The Layered Shield**
A shield or hexagon shape with visible internal layers (representing the 5 pillars). Each layer is a different shade of the primary blue. Symbolizes: protection (governance/security), structure (layered architecture), and solidity (reliable substrate). The top layer is slightly open, suggesting accessibility. Color palette: monochrome blues from #1B4F72 to #AED6F1. Style: clean, enterprise-ready, works for both open-source and commercial contexts.
+––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––-+

## 7.3 README Structure

The README is the most important marketing document. Structure:

-   **Line 1:** One-line description. "OAF makes AI workspaces persistent, inspectable, and transferable across models."

-   **Badges:** CI status, version, license, Discord.

-   **30-second pitch:** 3–4 sentences. The problem. The solution. The differentiator.

-   **Quick start:** brew install oaf && cd myproject && oaf init && oaf connect claude-code. Four commands.

-   **2-minute demo:** GIF or video. Show resume, handoff, remote access.

-   **Why not just use X?:** Table. For each competitor: what it does, what it doesn't, how OAF complements.

-   **Architecture overview:** ASCII diagram link to docs/architecture.md.

-   **Roadmap link:** Now / Next / Later / Not Planned.

-   **Contributing link:** How to set up, conventions, first-issue labels.

## 7.4 Wording Guidelines

-   **Use:** workspace substrate, persistent, inspectable, transferable, governed, model-agnostic, resume, handoff, cross-model, local-first.

-   **Avoid:** AI operating system, autonomous, magic, intelligent, revolutionary, next-generation, platform (until V2+), multi-agent (until V2+).

-   **Tone:** Technical, precise, restrained. Let the demo speak. Never claim capabilities that aren't shipped and benchmarked.

## 7.5 Communication Calendar

  ––––––––- –––––––––––––––––––––––- ––––––––––––––––– ––––––––––––––––––––––––––––––––––––––––––––––
  **When**          **What**                                        **Where**                          **Content**

  **Week 0**        Repo goes public with charter + architecture    GitHub, Twitter/X, Hacker News     \"We\'re building the missing workspace layer for AI coding tools.\" Show the problem.

  **V0.1 launch**   First usable release with resume + MCP memory   HN, Reddit r/programming, dev.to   30-second demo GIF. Benchmark: resume time. \"Try it on your project.\"

  **V0.2 launch**   Cross-model handoff works                       Same + YouTube demo                Split-screen video. Claude→Cursor handoff. \"Your project remembers, you don\'t have to.\"

  **V0.3 launch**   Remote gateway + Claude.ai skill                Same + Product Hunt                Phone→laptop demo. \"Your workspace, from anywhere.\" Claude skill template.

  **V1.0 launch**   Stable substrate                                Conference talks, blog posts       Benchmarks report. Compatibility matrix. \"The workspace standard is ready.\"

  **V2.0 launch**   Multi-agent                                     Same + enterprise outreach         Multi-agent demo. \"The Forge ignites.\" Open commercial tier.
  ––––––––- –––––––––––––––––––––––- ––––––––––––––––– ––––––––––––––––––––––––––––––––––––––––––––––

## 7.6 Community Building

-   **Discord server:** Channels: #general, #help, #showcase, #rfcs, #contributors.

-   **First issues:** Label good-first-issue on 10+ issues at launch. Include: docs improvements, test coverage, platform compatibility.

-   **Showcase:** Monthly "Built with OAF" showcase in Discord and on the repo wiki.

-   **RFC engagement:** Public RFCs for every significant change. Comment period before merge.

# 8. Next Steps & Action Plan

Week-by-week plan from today to V0.1 launch.

  –––––– –––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––– ––––––––––––––––––––––––-
  **Week**     **Deliverables**                                                                                                             **Go/No-Go**

  **1**        ADR-001 (language). Repo scaffolded: README, CONTRIBUTING, GOVERNANCE, ROADMAP, docs/. CI pipeline green on empty project.   Repo is public. ADR-001 decided.

  **2**        oaf init works for Python + Node. DevContainer template. Runtime manifest generation.                                        oaf init creates valid .oaf/ on a real project.

  **3**        oaf resume + oaf doctor. Named volume cache persistence. Snapshot/restore flow.                                              Resume is measurably faster than cold start.

  **4**        MCP memory server (SQLite + FTS5). write_memory, search_memory, log_decision, get_handoff_summary via stdio MCP.             Claude Code can read/write memory via MCP.

  **5**        oaf connect. Event log (JSONL). oaf state. Integration tests.                                                                Cursor/Windsurf can also connect.

  **6**        E2E tests. Benchmark suite. Documentation polish. V0.1 release.                                                              V0.1 tagged. Demo video published.

  **7–10**    V0.2: Actor/session model. Handoff summaries. oaf context, import, export.                                                   Cross-model handoff demonstrated.

  **11–16**   V0.3: Gateway + remote. Policy engine. Auth. Deployment template.                                                            Remote model writes decisions via HTTPS.

  **17–22**   V0.4: Memory hardening. Recovery. OAuth. Rate limiting.                                                                      Recovery trusted after .oaf/ corruption.

  **23–26**   V1.0: Stable contracts. Compatibility matrix. Reference demos. Claude.ai skill.                                              Third party adopts without guidance.
  –––––– –––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––– ––––––––––––––––––––––––-

Annexes

A. Glossary

  ––––––––– –––––––––––––––––––––––––––––––––––––––––––––-
  **Term**           **Definition**

  **MCP**            Model Context Protocol. Open standard by Anthropic for AI tool interoperability.

  **SSE**            Server-Sent Events. HTTP-based streaming protocol used for remote MCP transport.

  **FTS5**           SQLite Full-Text Search extension version 5. Enables fast text search in SQLite.

  **DevContainer**   Development Containers. VS Code standard for reproducible containerized dev environments.

  **ULID**           Universally Unique Lexicographically Sortable Identifier. Used for record IDs.

  **JSONL**          JSON Lines. One JSON object per line. Used for append-only event logs.

  **WAL**            Write-Ahead Logging. SQLite journal mode enabling concurrent reads during writes.

  **ADR**            Architectural Decision Record. Documents a significant technical decision.

  **RFC**            Request for Comments. Proposal document for significant changes.

  **RBAC**           Role-Based Access Control. Authorization model based on user/agent roles.

  **sqlite-vss**     SQLite Vector Similarity Search. Extension for embedding-based search.

  **rmcp**           Rust MCP. Rust crate for implementing MCP servers and clients.
  ––––––––– –––––––––––––––––––––––––––––––––––––––––––––-

B. Sources

Web research conducted March 9, 2026. Key sources:

-   DEV Community: "Cursor vs Claude Code vs Windsurf: Context Loss" (March 2026)

-   DEV Community: "How I synced Cursor, Claude, Windsurf with one shared brain (MCP)" — Nucleus MCP (Feb 2026)

-   DEV Community: "Self-managing memory system for Claude Code" (March 2026)

-   Anthropic: Claude Code Memory documentation (code.claude.com/docs/en/memory)

-   Google Developers Blog: "Architecting context-aware multi-agent framework" — ADK (Dec 2025)

-   n8n Blog: "AI Agent Orchestration Frameworks" (Oct 2025)

-   CIO: "21 agent orchestration tools" (March 2026)

-   Medium: "Cursor vs Claude Code" (March 2026)

-   NxCode: "Cursor vs Windsurf vs Claude Code 2026" (Feb 2026)

-   npm: \@modelcontextprotocol/server-memory (Jan 2026)

-   GitHub: mcp-ai-memory, Nucleus MCP, mem0/OpenMemory

-   OpenAI: Agents SDK Handoffs documentation

*End of Document*


---

*End of Project Bible v3. For the formatted DOCX version, see [project-bible-v3.docx](project-bible-v3.docx).*
