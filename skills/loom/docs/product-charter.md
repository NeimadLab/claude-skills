# Product Charter

## Mission

Loom makes AI-assisted development persistent, inspectable, and transferable across models, so technical users can resume real work instead of rebuilding context every time.


## Why "Loom"?

A loom weaves separate threads into a single, coherent fabric. That is exactly what this tool does — it weaves together the threads of context, environment, decisions, and governance that AI-assisted work produces, turning fragmented sessions into continuous, inspectable work.

The metaphor scales with the product:

| Phase | The Loom Metaphor |
|-------|-------------------|
| V0.1 | **The thread persists.** Your workspace context survives across sessions — nothing unravels when you close your laptop. |
| V0.2 | **Threads transfer.** Context woven by one model can be picked up by another. Claude's thread, Cursor's thread — same fabric. |
| V0.3 | **The loom is accessible.** Weave from anywhere — your phone, a remote server, a CI pipeline — the fabric stays in one place. |
| V1.0 | **The fabric is strong.** Stable, tested, documented. Third parties can weave on it. |
| V2.0 | **Multiple looms, one cloth.** Parallel agents weave simultaneously on isolated tracks, merging cleanly. |
| V3.0 | **The tapestry.** Coordinated actors — builder, reviewer, auditor — each weaving their specialty into one coherent output. |

The name is short (4 letters), memorable, evokes craftsmanship over hype, and avoids the AI-buzzword trap. The CLI command `loom` reads naturally: `loom init`, `loom resume`, `loom connect`.

## The Five Friction Points

Every AI coding tool loses your work in five specific, documented ways. Loom exists to solve all five.

### F1: Context Amnesia
The model forgets practical context mid-session or across sessions. Claude Code compacts without warning, losing decisions made 90 minutes ago. Cursor fragments context across tabs. Windsurf degrades in long sessions. No tool has solved persistent project memory.

**Loom's answer:** Structured project memory in SQLite with FTS5 search. Every decision, goal, risk, and observation is stored, typed, and searchable. Memory survives sessions, tool switches, and compaction events.

### F2: Environment Rebuild Tax
Every new session starts cold. Package reinstalls, configuration rediscovery, state reconstruction. Developers report 5–15 minutes of setup overhead per session restart. Multiplied by 3–5 restarts per day, this is 30–75 minutes of daily lost productivity.

**Loom's answer:** Runtime identity computation and cache persistence via named Docker volumes. `loom resume` detects drift and restores the environment in seconds, not minutes.

### F3: Cross-Model Blindness
Developers increasingly use multiple AI tools — Claude Code for deep architecture, Cursor for daily coding, Windsurf for iterative flows. Context does not transfer between them. Each tool starts from zero. Manual copy-paste of "brain state" across tabs.

**Loom's answer:** MCP-native memory server. Any MCP-compatible client (Claude Code, Cursor, Windsurf, Claude.ai, ChatGPT) can read and write to the same project memory. Decisions made in Claude Code are immediately available in Cursor.

### F4: Zero Governance
Remote models accessing local filesystems have no standard policy framework. DevContainers provide isolation but not governance. No audit trail, no approval workflow, no secret protection. Every shell command is an ungoverned action.

**Loom's answer:** YAML-based policy engine with action classes (read, write, execute, secret). Default-deny for sensitive operations. Session leases with expiration. Append-only audit trail on every action. Different policy scopes for local vs remote clients.

### F5: No Handoff Protocol
When one model hands off to another (or to the same model in a new session), there is no structured way to transfer: current goal, recent decisions, changed files, open risks, next actions. The handoff is either manual prompt engineering or nothing.

**Loom's answer:** `loom_get_handoff_summary()` generates a structured transfer packet. `loom_get_context()` produces a compact project onboarding file. The receiving model gets structured JSON, not a wall of text.

## What Loom Is

- **A persistent workspace and runtime layer** — your environment, caches, and context survive across sessions
- **A bridge across models, sessions, and deliverables** — decisions made in Claude Code are available in Cursor, and vice versa
- **An inspectable system with explicit permissions** — every action is logged, every sensitive operation is policy-gated
- **A contributor-friendly open-source technical product** — clear architecture, documented invariants, and a welcoming contribution process
- **A local-first AND remote-capable substrate** — works on your laptop, deployable to a server, accessible from any AI client


## Why "Loom"?

A loom weaves separate threads into a single, coherent fabric. That is exactly what this tool does — it weaves together the threads of context, environment, decisions, and governance that AI-assisted work produces, turning fragmented sessions into continuous, inspectable work.

The metaphor scales with the product:

| Phase | The Loom Metaphor |
|-------|-------------------|
| V0.1 | **The thread persists.** Your workspace context survives across sessions — nothing unravels when you close your laptop. |
| V0.2 | **Threads transfer.** Context woven by one model can be picked up by another. Claude's thread, Cursor's thread — same fabric. |
| V0.3 | **The loom is accessible.** Weave from anywhere — your phone, a remote server, a CI pipeline — the fabric stays in one place. |
| V1.0 | **The fabric is strong.** Stable, tested, documented. Third parties can weave on it. |
| V2.0 | **Multiple looms, one cloth.** Parallel agents weave simultaneously on isolated tracks, merging cleanly. |
| V3.0 | **The tapestry.** Coordinated actors — builder, reviewer, auditor — each weaving their specialty into one coherent output. |

The name is short (4 letters), memorable, evokes craftsmanship over hype, and avoids the AI-buzzword trap. The CLI command `loom` reads naturally: `loom init`, `loom resume`, `loom connect`.

## The Five Friction Points

Every AI coding tool loses your work in five specific, documented ways. Loom exists to solve all five.

### F1: Context Amnesia
The model forgets practical context mid-session or across sessions. Claude Code compacts without warning, losing decisions made 90 minutes ago. Cursor fragments context across tabs. Windsurf degrades in long sessions. No tool has solved persistent project memory.

**Loom's answer:** Structured project memory in SQLite with FTS5 search. Every decision, goal, risk, and observation is stored, typed, and searchable. Memory survives sessions, tool switches, and compaction events.

### F2: Environment Rebuild Tax
Every new session starts cold. Package reinstalls, configuration rediscovery, state reconstruction. Developers report 5–15 minutes of setup overhead per session restart. Multiplied by 3–5 restarts per day, this is 30–75 minutes of daily lost productivity.

**Loom's answer:** Runtime identity computation and cache persistence via named Docker volumes. `loom resume` detects drift and restores the environment in seconds, not minutes.

### F3: Cross-Model Blindness
Developers increasingly use multiple AI tools — Claude Code for deep architecture, Cursor for daily coding, Windsurf for iterative flows. Context does not transfer between them. Each tool starts from zero. Manual copy-paste of "brain state" across tabs.

**Loom's answer:** MCP-native memory server. Any MCP-compatible client (Claude Code, Cursor, Windsurf, Claude.ai, ChatGPT) can read and write to the same project memory. Decisions made in Claude Code are immediately available in Cursor.

### F4: Zero Governance
Remote models accessing local filesystems have no standard policy framework. DevContainers provide isolation but not governance. No audit trail, no approval workflow, no secret protection. Every shell command is an ungoverned action.

**Loom's answer:** YAML-based policy engine with action classes (read, write, execute, secret). Default-deny for sensitive operations. Session leases with expiration. Append-only audit trail on every action. Different policy scopes for local vs remote clients.

### F5: No Handoff Protocol
When one model hands off to another (or to the same model in a new session), there is no structured way to transfer: current goal, recent decisions, changed files, open risks, next actions. The handoff is either manual prompt engineering or nothing.

**Loom's answer:** `loom_get_handoff_summary()` generates a structured transfer packet. `loom_get_context()` produces a compact project onboarding file. The receiving model gets structured JSON, not a wall of text.

## What Loom Is Not

- **Not** a vague all-purpose autonomous agent platform
- **Not** a concurrency-first experiment with weak guarantees
- **Not** a magical black box that hides state and authority
- **Not** a large unscoped framework trying to support every workflow from day one
- **Not** a replacement for your IDE, your version control, or your CI/CD pipeline

## Core Principles

| Principle | Implication | Enforced How |
|-----------|-------------|-------------|
| **Continuity before autonomy** | The first value is "restart less from zero", not "do more alone" | V0.1 focuses on resume, not orchestration |
| **Inspectability before magic** | Hidden complexity is acceptable. Hidden authority is not. | Every action logged to events.jsonl |
| **Filesystem and Git before derived metadata** | `.loom/` accelerates and explains, never becomes canonical truth | Reconciliation rule in architecture |
| **Sequential before parallel** | Reliable handoff before simultaneous writing | One-writer invariant until V2.0 |
| **Explicit permissions** | Secret access, installs, and shell execution are policy-governed | Policy engine with YAML rules |
| **Practical power, simple surfaces** | Technical users accept complexity if the main interface is clean | CLI-first, minimal mandatory config |
| **MCP-native** | All model interactions use standard protocol | No custom wire formats, ever |

## Target Users

| Segment | Pain Point | What They Do Today | Loom Fit | When |
|---------|-----------|-------------------|---------|------|
| **Solo technical builder** | Rebuilds env every session. Loses context between tools. | Manual CLAUDE.md. Copy-paste between tools. | Excellent | V0.1 |
| **Small engineering team** | No structured handoff between team members or their AI tools. | Shared Notion docs. Tribal knowledge. | Strong | V0.3+ (remote) |
| **AI-heavy product team** | Switches models frequently. Context doesn't transfer. | Multiple tool subscriptions. Manual bridging. | Strong | V0.2+ |
| **Enterprise / regulated org** | Needs audit trails, governance, approved model access. | Bespoke internal tooling or nothing. | V1.0+ | V1.0 (policy + audit) |

## Strategic Positioning

Loom occupies a unique niche: the intersection of workspace persistence, cross-model memory, and governed access. No existing tool covers all three:

- **Claude Code CLAUDE.md** covers persistence but not cross-model or governance
- **Nucleus MCP** covers cross-model memory but not runtime or governance
- **DevContainers** cover runtime but not memory or governance
- **LangGraph/CrewAI** cover orchestration but are cloud-first, not workspace-native

Loom is the integration layer that unifies these concerns under one coherent, local-first (and remote-capable) substrate.

## Timing

The window is 12–18 months. MCP became the standard in late 2024. AI coding tools have proven their value but haven't solved persistence. Major vendors will eventually absorb these capabilities natively. Loom must establish itself as the neutral, open-source workspace standard before that happens.

If Loom is absorbed, the mission succeeded — the standard was set.
