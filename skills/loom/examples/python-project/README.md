# Example: Python Project with Loom

This directory shows what a Python project looks like after `loom init`.

## What Loom created

> **Note:** `memory.db` is not committed to Git (it's a binary SQLite file).
> Run `loom init` in this directory to create it.

```
.loom/
├── runtime.json    ← Runtime identity (hash of lockfiles + tool versions)
├── memory.db       ← SQLite database with FTS5 (project memory)
└── events.jsonl    ← Append-only event log
```

## Try it yourself

```bash
cd examples/python-project
loom init          # Creates .loom/ (skips if exists)
loom state         # Shows workspace snapshot
loom doctor        # Runs health checks

# Connect an AI tool
loom connect claude-code

# Now Claude Code can search/write memory via MCP:
#   loom_search_memory(query="auth")
#   loom_log_decision(decision="Use JWT", rationale="Stateless, scalable")
```

## What .loom/ contains after use

After a few sessions with different AI tools:

```
.loom/
├── runtime.json         ← Detects if your lockfiles or tool versions changed
├── memory.db            ← 15 entries: 5 decisions, 3 goals, 2 risks, 5 notes
├── events.jsonl         ← 47 events: inits, memory writes, decisions logged
└── (no other files)     ← Everything else is derived from these three
```

The memory.db is a standard SQLite file. You can inspect it directly:

```bash
sqlite3 .loom/memory.db "SELECT type, status, content FROM memory ORDER BY timestamp DESC LIMIT 5;"
```
