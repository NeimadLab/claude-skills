"""Team authentication and user identity.

Supports solo (no auth / single key) and team (multi-key with user identity) modes.
Designed for small teams (3-10 devs). For >20 concurrent users, migrate to PostgreSQL.

Modes:
- solo:     No auth or single LOOM_API_KEY. All writes attributed to actor name only.
- team:     .loom/team/keys.json maps API keys to users. Writes attributed to user + actor.

Limits (documented, not hidden):
- SQLite WAL supports ~5 concurrent writers safely, ~50 concurrent readers.
- Write token ensures single-writer at application level.
- For >20 users or >10K memory entries, consider PostgreSQL migration (V2.0).
"""

from __future__ import annotations

import json
import secrets
from datetime import UTC, datetime
from pathlib import Path

from loom.constants import loom_dir


def _team_dir(workspace: Path) -> Path:
    """Return the team configuration directory."""
    d = loom_dir(workspace) / "team"
    d.mkdir(parents=True, exist_ok=True)
    return d


def _keys_path(workspace: Path) -> Path:
    """Return the path to the team keys file."""
    return _team_dir(workspace) / "keys.json"


def _load_keys(workspace: Path) -> dict:
    """Load team keys. Returns {api_key: {user_id, name, role, created_at}}."""
    kp = _keys_path(workspace)
    if not kp.exists():
        return {}
    return json.loads(kp.read_text())


def _save_keys(workspace: Path, keys: dict) -> None:
    """Save team keys."""
    _keys_path(workspace).write_text(json.dumps(keys, indent=2) + "\n")


def is_team_mode(workspace: Path | None = None) -> bool:
    """Check if workspace is in team mode (has keys.json with entries)."""
    root = workspace or Path.cwd()
    keys = _load_keys(root)
    return len(keys) > 0


def add_user(
    name: str,
    role: str = "member",
    workspace: Path | None = None,
) -> dict:
    """Add a team member and generate their API key.

    Roles:
    - admin:  can add/remove users, promote/reject, manage policies
    - member: can read/write memory, open sessions, log decisions
    - viewer: can read memory and context, cannot write

    Returns: {api_key, user_id, name, role}
    """
    root = workspace or Path.cwd()
    keys = _load_keys(root)

    api_key = secrets.token_hex(32)
    user_id = secrets.token_hex(8)

    keys[api_key] = {
        "user_id": user_id,
        "name": name,
        "role": role,
        "created_at": datetime.now(UTC).isoformat(),
    }

    _save_keys(root, keys)

    return {"api_key": api_key, "user_id": user_id, "name": name, "role": role}


def remove_user(user_id: str, workspace: Path | None = None) -> bool:
    """Remove a team member by user_id."""
    root = workspace or Path.cwd()
    keys = _load_keys(root)

    to_remove = [k for k, v in keys.items() if v["user_id"] == user_id]
    if not to_remove:
        return False

    for k in to_remove:
        del keys[k]

    _save_keys(root, keys)
    return True


def list_users(workspace: Path | None = None) -> list[dict]:
    """List all team members (without exposing API keys)."""
    root = workspace or Path.cwd()
    keys = _load_keys(root)

    return [
        {
            "user_id": v["user_id"],
            "name": v["name"],
            "role": v["role"],
            "created_at": v.get("created_at", "unknown"),
            "key_prefix": k[:8] + "...",
        }
        for k, v in keys.items()
    ]


def authenticate(api_key: str, workspace: Path | None = None) -> dict | None:
    """Authenticate a request by API key. Returns user info or None.

    In solo mode (no keys.json), falls back to LOOM_API_KEY env var check.
    """
    root = workspace or Path.cwd()
    keys = _load_keys(root)

    if not keys:
        # Solo mode — no team keys, defer to gateway's env var check
        return None

    user = keys.get(api_key)
    if user:
        return {
            "user_id": user["user_id"],
            "name": user["name"],
            "role": user["role"],
        }

    return None  # Invalid key


def check_permission(user: dict | None, action: str) -> bool:
    """Check if a user has permission for an action.

    Actions: read, write, admin
    If user is None (solo mode), all actions are allowed.
    """
    if user is None:
        return True  # Solo mode = no restrictions

    role = user.get("role", "viewer")

    permissions = {
        "admin": {"read", "write", "admin"},
        "member": {"read", "write"},
        "viewer": {"read"},
    }

    return action in permissions.get(role, set())


# ── Limits Documentation ──────────────────────────────────────

TEAM_LIMITS = """
Loom Team Mode — Known Limits

Current (SQLite backend, V0.x):
  ✅ 3-10 concurrent users      Works well with WAL mode
  ⚠️  10-20 concurrent users     May see occasional write contention
  ❌ >20 concurrent users        Requires PostgreSQL migration (V2.0)

  ✅ <10,000 memory entries       FTS5 search <1ms at p95
  ⚠️  10K-100K entries            FTS5 still fast, but decay/rebuild slower
  ❌ >100K entries                Consider archiving or PostgreSQL

  ✅ 1 workspace per server       Current architecture
  ✅ Multi-workspace via router   V0.3+ with workspace router

  ✅ API key auth                 Good for small teams
  ⚠️  No SSO/OAuth               Planned for V1.0
  ❌ No RBAC beyond 3 roles      Planned for V2.0

Migration path to V2.0 (PostgreSQL):
  - Storage abstraction layer (MemoryStore interface)
  - PostgreSQL backend implementation
  - Connection pooling for concurrent access
  - Full RBAC with custom roles
"""
