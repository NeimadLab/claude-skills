# ADR-000: Why Loom Exists

## Status
Accepted

## Context
Multiple tools partially solve the AI workspace persistence problem: Claude Code has CLAUDE.md and auto-memory, Nucleus MCP provides shared memory across tools, DevContainers provide reproducible environments, and mem0/OpenMemory provide semantic memory. A reasonable question is: why not just combine these existing tools?

## Decision
Loom exists because no existing tool provides the unified integration of all five capabilities required for a complete AI workspace substrate: context persistence, environment persistence, cross-model transfer, governed access, and structured handoff. Each existing tool covers 1-2 of these concerns but leaves the others unaddressed, creating a fragmented experience that requires manual bridging.

The specific integration value Loom provides:
1. **Runtime + Memory unified** — DevContainers handle env, but don't know about project decisions. Loom ties them together.
2. **Memory + Governance unified** — Nucleus MCP shares memory, but has no policy engine. A remote model with memory access but no governance is a security risk.
3. **Local + Remote unified** — No existing tool provides the same workspace substrate accessible from both local (stdio) and remote (SSE/HTTPS) clients with consistent policy enforcement.
4. **Handoff as a first-class concept** — Existing tools treat handoff as an afterthought. Loom makes it a structured, testable operation.

## Consequences
- **Loom must prove this integration value quickly** — if any two existing tools merge their capabilities, Loom's niche shrinks.
- **Loom should leverage, not reinvent** — use MCP as the protocol, SQLite as proven storage, DevContainers as the runtime spec. Build the integration layer, not the components.
- **The bar is higher** — Loom must be better than "install Nucleus + DevContainers + a memory MCP server" for the same use case. If it isn't, it shouldn't exist.
