
# Connect Loom to Cursor

## Automatic Setup

```bash
cd ~/your-project
loom connect cursor
```

This writes to `~/.cursor/mcp.json`. Restart Cursor to activate.

## Manual Setup

Edit `~/.cursor/mcp.json` (create the file if it doesn't exist):

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

## Project-Scoped Configuration

Create `.cursor/mcp.json` in your project root for project-scoped configuration.

## Verify Connection

Open Cursor's AI panel and ask:

```
Search loom memory for anything
```

Cursor should invoke `loom_search_memory` via MCP.

## Cross-Model Workflow

The most powerful Loom use case with Cursor:

1. Do deep architecture work in **Claude Code** — log decisions via `loom_log_decision`
2. Switch to **Cursor** for implementation — Cursor reads the same decisions
3. Ask Cursor: *"What decisions have been made about auth?"* → it searches Loom memory
4. Cursor implements based on the decisions Claude Code recorded

No context is lost in the switch.
