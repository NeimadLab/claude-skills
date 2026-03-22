
# Local Setup Guide

Complete guide to running Loom on your local machine with every supported AI tool.

## Installation

### macOS / Linux

```bash
pip install loom
```

Or with [pipx](https://pipx.pypa.io/) for isolated installation (recommended):

```bash
pipx install loom
```

### Windows

```powershell
pip install loom
```

### From source (for contributors)

```bash
git clone https://github.com/NeimadLab/loom.git
cd loom
pip install -e ".[dev]"
```

## Initialize a Workspace

```bash
cd ~/your-project
loom init
```

Loom creates `.loom/` and detects your project type from marker files:

| Project Type | Detected From | Lockfiles Tracked |
|-------------|---------------|-------------------|
| Python | `pyproject.toml`, `setup.py`, `requirements.txt` | `poetry.lock`, `Pipfile.lock`, `requirements.txt` |
| Node | `package.json` | `package-lock.json`, `yarn.lock`, `pnpm-lock.yaml` |
| Rust | `Cargo.toml` | `Cargo.lock` |
| Go | `go.mod` | `go.sum` |

Loom also adds `.loom/` to your `.gitignore` automatically.

## Connect AI Tools

### Quick Auto-Setup

```bash
loom connect claude-code    # writes to ~/.claude/settings.json
loom connect cursor          # writes to ~/.cursor/mcp.json
loom connect windsurf        # writes to ~/.codeium/windsurf/mcp_config.json
```

Each command writes the MCP server configuration to the tool's config file and tells you to restart the tool.

### Manual Configuration

If `loom connect` doesn't find your config file, or you want to configure manually, see the tool-specific guides below.

## Verify the Connection

After restarting your AI tool, verify the connection:

1. Open a conversation in the tool
2. Ask: *"What Loom tools are available?"* or *"Search loom memory for anything"*
3. The tool should call `loom_search_memory` and return results (empty is fine for a new workspace)

If the tool doesn't see Loom, check:

- The tool was restarted after `loom connect`
- The `loom` command is on your PATH (run `which loom` to verify)
- The config file was written to the correct location (check the output of `loom connect`)

## Daily Workflow

```bash
# Start of day: check workspace health
loom resume          # verifies environment hasn't drifted
loom doctor          # checks everything is healthy

# During work: your AI tool logs decisions via MCP automatically

# End of day: review what happened
loom events          # see recent activity
loom search ""       # browse all memory entries

# After updating dependencies
loom resume          # detects lockfile changes, updates identity

# After git pull
loom resume          # detects any drift from upstream changes
```

## Troubleshooting

### "loom: command not found"

Your Python scripts directory isn't on your PATH. Fix:

```bash
# Find where pip installed it
pip show loom | grep Location

# Add to PATH (add to ~/.bashrc or ~/.zshrc)
export PATH="$HOME/.local/bin:$PATH"
```

### MCP tools not appearing in my AI tool

1. Verify Loom is installed: `loom --version`
2. Verify the config was written: check the path shown by `loom connect`
3. Restart the AI tool completely (not just the conversation)
4. Check the tool's MCP logs for connection errors

### "No workspace found"

You need to run `loom init` in the project directory first. Loom looks for `.loom/` in the current directory.

### Runtime identity drift

This means your lockfiles or tool versions changed since the last `loom init`. It's usually fine — just means your environment evolved. Run `loom init --force` to re-baseline if needed.
