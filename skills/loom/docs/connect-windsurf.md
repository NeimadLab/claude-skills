
# Connect Loom to Windsurf

## Automatic Setup

```bash
cd ~/your-project
loom connect windsurf
```

This writes to `~/.codeium/windsurf/mcp_config.json`. Restart Windsurf to activate.

## Manual Setup

Edit `~/.codeium/windsurf/mcp_config.json`:

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

## Verify Connection

In Windsurf's Cascade panel, ask:

```
What loom tools are available?
```

Windsurf should discover the 6 Loom MCP tools.

## Working with Windsurf Memories

Windsurf has its own "Memories" feature that stores workspace facts. Loom and Windsurf Memories are complementary:

- **Windsurf Memories** — automatic, Windsurf-only, ephemeral per workspace
- **Loom memory** — structured, cross-tool, persistent, searchable

You can use both. Loom adds cross-model transfer and structured decision tracking that Windsurf Memories don't provide.
