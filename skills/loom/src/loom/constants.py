"""Paths, defaults, and constants."""

from pathlib import Path

OAF_DIR = ".loom"
MEMORY_DB = "memory.db"
INVENTORY_DB = "inventory.db"
EVENTS_FILE = "events.jsonl"
RUNTIME_MANIFEST = "runtime.json"
SNAPSHOT_FILE = "snapshot.json"

SUPPORTED_PROJECTS = {
    "python": ["pyproject.toml", "setup.py", "requirements.txt", "Pipfile", "poetry.lock"],
    "node": ["package.json"],
    "rust": ["Cargo.toml"],
    "go": ["go.mod"],
}

LOCKFILES = {
    "python": ["poetry.lock", "Pipfile.lock", "requirements.txt"],
    "node": ["package-lock.json", "yarn.lock", "pnpm-lock.yaml", "bun.lockb"],
    "rust": ["Cargo.lock"],
    "go": ["go.sum"],
}

CACHE_VOLUME_PATHS = {
    "python": ["~/.cache/pip", ".venv"],
    "node": ["node_modules", "~/.npm"],
    "rust": ["~/.cargo/registry", "target"],
    "go": ["~/go/pkg/mod"],
}

MCP_CLIENT_CONFIGS = {
    "claude-code": {
        "path_candidates": ["~/.claude/settings.json", "~/.claude.json"],
        "key": "mcpServers",
    },
    "cursor": {
        "path_candidates": ["~/.cursor/mcp.json"],
        "key": "mcpServers",
    },
    "windsurf": {
        "path_candidates": ["~/.codeium/windsurf/mcp_config.json"],
        "key": "mcpServers",
    },
}


def loom_dir(workspace: Path | None = None) -> Path:
    """Return the .loom directory for a workspace."""
    base = workspace or Path.cwd()
    return base / OAF_DIR


def ensure_loom_dir(workspace: Path | None = None) -> Path:
    """Create and return the .loom directory."""
    d = loom_dir(workspace)
    d.mkdir(parents=True, exist_ok=True)
    return d
