
# Getting Started with Loom

This guide gets you from zero to a working Loom workspace in 5 minutes.

## Prerequisites

- **Python 3.11+** — check with `python3 --version`
- **Git** — check with `git --version`
- **An AI coding tool** — at least one of: Claude Code, Cursor, Windsurf, Claude Desktop, or Claude.ai

Docker is optional but recommended for runtime persistence (V0.2+).

## Step 1: Install Loom

```bash
# From PyPI (recommended)
pip install loom

# Or from source
git clone https://github.com/NeimadLab/loom.git
cd loom
pip install -e .
```

Verify the installation:

```bash
loom --version
# loom, version 0.2.0
```

## Step 2: Initialize Your Project

Navigate to any project directory and run:

```bash
cd ~/my-project
loom init
```

Loom detects your project type (Python, Node, Rust, Go) and creates a `.loom/` directory with:

| File | Purpose |
|------|---------|
| `runtime.json` | Deterministic hash of your environment (lockfiles, tool versions) |
| `memory.db` | SQLite database with FTS5 search — stores decisions, goals, risks, notes |
| `events.jsonl` | Append-only log of every action (for audit and reconstruction) |

## Step 3: Connect Your AI Tool

```bash
loom connect claude-code
# or
loom connect cursor
# or
loom connect windsurf
```

This writes the MCP server configuration to your tool's config file. **Restart the tool** to activate the connection.

For tool-specific details, see:

- [Connect Claude Code](connect-claude-code.md)
- [Connect Cursor](connect-cursor.md)
- [Connect Windsurf](connect-windsurf.md)
- [Connect Claude Desktop](connect-claude-desktop.md)
- [Connect Claude.ai (remote)](setup-cloud.md)
- [Connect ChatGPT (remote)](connect-chatgpt.md)

## Step 4: Use Loom

### From your AI tool (via MCP)

Once connected, your AI tool automatically has access to Loom's MCP tools. You can ask it:

- *"Search my project memory for auth decisions"* → calls `loom_search_memory`
- *"Log a decision: Use JWT with RS256 for authentication"* → calls `loom_log_decision`
- *"Give me a handoff summary so I can continue where we left off"* → calls `loom_get_handoff_summary`
- *"What's the current project context?"* → calls `loom_get_context`

### From the terminal (CLI)

```bash
# Search project memory
loom search "authentication"

# Log a decision directly
loom log "Use PostgreSQL for the database" --rationale "ACID, JSON support, mature"

# View recent events
loom events

# Check workspace health
loom doctor

# View workspace state
loom state

# Resume after interruption (checks runtime identity drift)
loom resume
```

## Step 5: Cross-Model Handoff

The magic of Loom is that context transfers across tools:

1. **Work in Claude Code** — make architectural decisions, log them via MCP
2. **Switch to Cursor** — Cursor reads the same memory, sees the same decisions
3. **Open Claude.ai on your phone** (remote setup) — brainstorm, persist decisions
4. **Back to Claude Code** — everything is there, structured, searchable

No copy-paste. No prompt scaffolding. One persistent memory, accessible from any MCP-compatible tool.

## What's Next

- [Local Setup Guide](setup-local.md) — detailed local configuration
- [Cloud Setup Guide](setup-cloud.md) — deploy Loom on a server for remote access
- [MCP Tool Reference](mcp-tool-reference.md) — all 6 MCP tools with parameters and examples
- [Memory Model](memory-model.md) — how structured memory works
- [Architecture](architecture.md) — the five pillars of Loom
