
# Connect Loom to Claude Desktop

Claude Desktop (the macOS/Windows application) supports MCP servers through its configuration file.

## Setup

### macOS

Edit `~/Library/Application Support/Claude/claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "loom": {
      "command": "loom",
      "args": ["mcp", "serve"],
      "env": {
        "LOOM_WORKSPACE": "/absolute/path/to/your/project"
      }
    }
  }
}
```

### Windows

Edit `%APPDATA%\Claude\claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "loom": {
      "command": "loom",
      "args": ["mcp", "serve"],
      "env": {
        "LOOM_WORKSPACE": "C:\\Users\\you\\projects\\your-project"
      }
    }
  }
}
```

**Important:** Claude Desktop requires an absolute path to the workspace because it doesn't run in your project directory. Set `LOOM_WORKSPACE` to point to the project that has been initialized with `loom init`.

### Restart

Quit and reopen Claude Desktop completely. The MCP server starts when the app launches.

## Verify

In Claude Desktop, ask:

```
What loom tools do you have access to?
```

Claude should list the 6 Loom tools (search_memory, write_memory, log_decision, get_handoff_summary, get_context, get_state).

## Use Case

Claude Desktop is great for quick interactions — reviewing project state, brainstorming decisions, and logging insights without opening your IDE. The decisions you log from Claude Desktop are immediately available when you switch to Claude Code, Cursor, or Windsurf.

## Multiple Projects

To switch between projects, update the `LOOM_WORKSPACE` path and restart Claude Desktop. Multi-project support via `loom_set_project` is planned for V0.3.
