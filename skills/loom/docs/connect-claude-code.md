
# Connect Loom to Claude Code

## Automatic Setup

```bash
cd ~/your-project
loom connect claude-code
```

This writes to `~/.claude/settings.json`. Restart Claude Code to activate.

## Manual Setup

Edit `~/.claude/settings.json`:

```json
{
  "mcpServers": {
    "loom": {
      "command": "loom",
      "args": ["mcp", "serve"]
    }
  }
}
```

If you already have other MCP servers configured, add the `"loom"` entry alongside them.

## Project-Scoped Configuration

To scope Loom to a specific project (instead of globally), create `.claude/settings.json` in your project root:

```json
{
  "mcpServers": {
    "loom": {
      "command": "loom",
      "args": ["mcp", "serve"]
    }
  }
}
```

Project-level settings override user-level settings for that project.

## Using Loom with CLAUDE.md

Loom complements CLAUDE.md. You can add a section to your project's `CLAUDE.md`:

```markdown
## Project Memory

This project uses Loom for persistent memory. Use these MCP tools:

- `loom_search_memory` — search before making decisions (avoid duplicates)
- `loom_log_decision` — log every architectural or technical decision
- `loom_get_handoff_summary` — read this at the start of every session
- `loom_get_context` — get a compact project overview
```

## Migrating from CLAUDE.md to Loom

If you have an existing CLAUDE.md with decisions and conventions:

```bash
loom import CLAUDE.md
```

This parses your CLAUDE.md and imports instructions as structured memory entries. You can then export back:

```bash
loom export claude-md
```

## Verify Connection

In Claude Code, run:

```
> Search loom memory for anything
```

Claude Code should call `loom_search_memory` and return results. If it's a fresh workspace, the result will be empty — that's expected.

## Available MCP Tools

Once connected, Claude Code can use these tools:

| Tool | What It Does |
|------|-------------|
| `loom_search_memory` | Search decisions, notes, goals, risks by keyword |
| `loom_write_memory` | Store a new memory entry (note, observation, artifact) |
| `loom_log_decision` | Record a decision with rationale |
| `loom_get_handoff_summary` | Get a structured summary for session onboarding |
| `loom_get_context` | Get compact project context (type, stack, goals, risks) |
| `loom_get_state` | Get workspace operational state |

## Tips

- Ask Claude Code to call `loom_get_handoff_summary` at the start of every session — this gives it full context from previous work.
- After making architectural decisions, ask Claude Code to log them with `loom_log_decision` including the rationale.
- Use `loom_search_memory` before making decisions to check if a related decision already exists.
- Memory entries are tagged with the actor name (`claude-code`), so you can track which tool made which decisions.
