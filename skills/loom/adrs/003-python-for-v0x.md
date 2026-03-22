# ADR-003: Python for V0.x Implementation

## Status
Accepted

## Context
The project charter and initial architecture documents discussed Rust or TypeScript as potential implementation languages. For V0.1, we needed to choose a language that:

1. Maximizes development speed for a solo/small team
2. Has mature MCP SDK support
3. Allows rapid iteration during the 0.x phase
4. Can be tested and contributed to by the widest audience

## Decision
V0.x is implemented in Python 3.11+ with:

- **Click** for CLI
- **Rich** for terminal output
- **mcp** (official Python SDK) for MCP server
- **SQLite3** (stdlib) for memory and state storage
- **ruff** for linting and formatting

The architecture is modular enough that individual components (e.g., the CLI entry point) could be rewritten in Rust for performance if the project reaches V1.0+ and startup latency becomes a real issue.

## Consequences
- **Easier:** Faster development. Larger contributor pool. Official MCP SDK. Rich ecosystem for prototyping.
- **Harder:** CLI startup is ~200ms (vs ~50ms for Rust). Not a single binary — requires Python runtime. Less suitable for embedding in other tools.
- **Migration path:** If V1.0 needs Rust performance, the MCP server and memory layer (SQLite) are portable. Only the CLI and glue code would need rewriting.
