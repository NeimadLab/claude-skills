# Risks, Anti-Patterns & Mitigations

## Risk Matrix

| Risk | Severity | Impact | Mitigation | Owner |
|------|----------|--------|------------|-------|
| **Vendor absorption** | Critical | Anthropic, GitHub, or OpenAI build native workspace persistence within 12 months | Move fast. V0.1 in 6 weeks. Position as cross-vendor neutral layer. If absorbed: the standard was set. | Maintainer |
| **Scope inflation** | Critical | Feature creep prevents V0.1 from shipping. Contributors pull in different directions. | Hard phase gates. Public "Not Planned" list. Single maintainer authority for V0.x scope. Say no early and often. | Maintainer |
| **MCP protocol drift** | High | MCP spec evolves and breaks Loom's gateway implementation | Use official MCP SDK. Contribute to the spec. Keep gateway tool surface minimal and versioned. Pin MCP SDK versions. | Gateway lead |
| **False confidence in memory** | High | AI-written memory entries become unreliable folklore that developers trust without verification | Status model (hypothesis/validated). Human-only promotion. Consultative semantics — memory never blocks actions. Decay policy for unvalidated entries (V0.4+). | Memory lead |
| **Security overreach** | High | Remote-to-local execution exploited for data exfiltration or arbitrary command execution | Default-deny for remote. Session leases with expiration. Mandatory approval for shell and secrets. Audit trail on every call. Security review before V0.3. | Security lead |
| **State corruption** | Medium | Derived state in `.loom/` drifts from repository reality, causing stale or conflicting information | Rebuild commands (`loom rebuild`). Canonical filesystem/Git rules. Event replay for reconstruction. Doctor checks for consistency. | State lead |
| **Docker dependency** | Medium | Some developers resist Docker. Reduces adoption for lightweight or mobile use cases. | Docker is recommended, not required. Support "native mode" with degraded capabilities (no runtime isolation). Clear docs on what degrades without Docker. | Runtime lead |
| **Premature concurrency** | Medium | Community demands or contributor PRs push shared-directory multi-writer before isolation is ready | Delay to V2.0 worktree-based isolation. Sequential-only invariant until proven. Explicit "Not Planned" entry. Close related issues with explanation. | Maintainer |
| **Contributor fragmentation** | Low | Too many PRs in too many directions. Architecture erodes through incremental exceptions. | RFC process for significant changes. ADRs for invariants. Clear CONTRIBUTING.md with scope guidance. Regular triage. | Maintainer |

## Anti-Patterns to Explicitly Avoid

### ⚠ "AI Operating System" Inflation

**What it looks like:** Marketing copy or README language that claims Loom is an "AI operating system" or "autonomous agent platform" during V0.x.

**Why it's dangerous:** It invites comparison with LangGraph, CrewAI, and Google ADK — frameworks that already do multi-agent orchestration well. Loom V0.x is not competing with them. It's solving a different problem (workspace persistence and handoff), and losing that positioning means losing the strategic niche.

**Rule:** Use precise language. V0.x is a "workspace substrate." V1.0 is a "workspace standard." V2.0+ can claim "multi-agent" capabilities.

### ⚠ Opaque Background Automation

**What it looks like:** Loom running hidden background processes, silent cleanups, or automatic memory updates that the user didn't explicitly request.

**Why it's dangerous:** Trust is Loom's most important asset. If users can't explain what Loom did, they won't trust it with their projects. This directly undermines the "inspectability" principle.

**Rule:** Every action must be explicit, evented, and inspectable. Hidden complexity is acceptable. Hidden authority is not. If it changes state, it must appear in the event log.

### ⚠ Memory-as-Truth

**What it looks like:** Loom (or models using Loom) treating `.loom/memory` as the source of truth instead of the filesystem and Git.

**Why it's dangerous:** Memory entries can be wrong, stale, or hallucinated. If they override canonical state, the workspace becomes unreliable.

**Rule:** Memory is consultative. It accelerates and explains. It never overrides filesystem + Git. The reconciliation rule is explicit: canonical sources always win.

### ⚠ Unrestricted Remote Shell

**What it looks like:** Remote models being able to execute arbitrary shell commands through the gateway by default.

**Why it's dangerous:** This is the highest-risk action in Loom. A compromised or misaligned model with shell access can exfiltrate data, install malware, or destroy the workspace.

**Rule:** Shell execution for remote clients is DENIED by default. Unlocking requires an explicit policy rule AND an approval flow. Even local shell execution is approval-gated.

### ⚠ Multi-Writer on Shared Directory

**What it looks like:** Allowing two or more AI agents to edit files concurrently in the same directory without isolation.

**Why it's dangerous:** Shared-directory multi-writer is deceptively hard. Merge conflicts, race conditions, and state corruption are guaranteed. Every premature multi-agent project in 2025 collapsed under this complexity.

**Rule:** Only safe with Git worktree isolation (V2.0). Never on a shared directory. The one-writer invariant holds until V2.0.

### ⚠ Plugin Sprawl Before Stable Core

**What it looks like:** Building an extension or plugin system before the core contracts are frozen at V1.0.

**Why it's dangerous:** Extensions invite scope creep, compatibility nightmares, and contributor confusion. The core must be stable before it can be extended.

**Rule:** Freeze core at V1.0. Extensions at V1.5+ earliest. The plugin API is not part of V1.0 scope.

### ⚠ Vanity Metrics in Benchmarks

**What it looks like:** Publishing benchmarks that measure the wrong things — e.g., "lines of code generated" instead of "workspace resume time" or "handoff quality."

**Why it's dangerous:** Vanity metrics erode credibility with technical users. Loom's value proposition is about persistence and continuity, not generation speed.

**Rule:** Benchmark what matters to the product claim. Resume latency. Handoff quality. Rebuild time. Memory search relevance. Policy evaluation speed.
