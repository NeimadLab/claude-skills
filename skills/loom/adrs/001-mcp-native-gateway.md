# ADR-001: MCP-Native Gateway

## Status
Accepted

## Context
Loom needs to expose workspace tools to AI models. We could design a custom protocol or adopt an existing standard. MCP (Model Context Protocol) has become the de facto standard for AI tool interoperability, supported by Claude Code, Cursor, Windsurf, VS Code, and OpenAI.

## Decision
All model-facing interactions in Loom will use the standard MCP protocol. The gateway will be an MCP server supporting stdio (local) and SSE/HTTPS (remote) transports. No custom wire protocols.

## Consequences
- **Easier:** Immediate compatibility with every MCP-capable client. Lower adoption friction. Community contributions align with a known standard.
- **Harder:** Constrained by MCP's capabilities. May need to wait for MCP spec evolution for advanced features. Must track MCP breaking changes.
