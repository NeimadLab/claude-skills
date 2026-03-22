"""Write token — lease-based single-writer exclusion.

Prevents concurrent writes to the workspace memory. One actor at a time.
Token expires after a configurable lease duration.
"""

from __future__ import annotations

import json
from datetime import UTC, datetime
from pathlib import Path

from loom.constants import loom_dir
from loom.events import emit
from loom.models import Event

DEFAULT_LEASE_MINUTES = 15
TOKEN_FILE = "write_token.json"


def _token_path(workspace: Path) -> Path:
    """Return the path to the write token file."""
    return loom_dir(workspace) / TOKEN_FILE


def _now() -> str:
    """Current UTC timestamp as ISO string."""
    return datetime.now(UTC).isoformat()


def _parse_ts(iso: str) -> datetime:
    """Parse an ISO timestamp."""
    return datetime.fromisoformat(iso)


def acquire(
    session_id: str,
    actor: str,
    workspace: Path | None = None,
    lease_minutes: int = DEFAULT_LEASE_MINUTES,
    force: bool = False,
) -> dict:
    """Acquire the write token for a session.

    Returns:
        {"acquired": True, ...} on success
        {"acquired": False, "holder": ..., "expires_at": ...} if held by another
    """
    root = workspace or Path.cwd()
    tp = _token_path(root)
    now = _now()

    # Check existing token
    if tp.exists() and not force:
        existing = json.loads(tp.read_text())

        # Check if expired
        expires = _parse_ts(existing["expires_at"])
        if datetime.now(UTC) < expires:
            # Still valid — reject unless same session
            if existing["session_id"] == session_id:
                # Renew the lease
                existing["expires_at"] = _compute_expiry(lease_minutes)
                existing["renewed_at"] = now
                tp.write_text(json.dumps(existing, indent=2) + "\n")
                return {"acquired": True, "renewed": True, **existing}

            return {
                "acquired": False,
                "reason": "held_by_another",
                "holder": existing["actor"],
                "holder_session": existing["session_id"],
                "expires_at": existing["expires_at"],
            }
        # Expired — reclaim
        emit(
            Event(
                event_type="write_token_expired",
                actor=existing["actor"],
                session_id=existing["session_id"],
                data={"expired_at": existing["expires_at"]},
            ),
            root,
        )

    # Acquire
    token = {
        "session_id": session_id,
        "actor": actor,
        "acquired_at": now,
        "expires_at": _compute_expiry(lease_minutes),
        "lease_minutes": lease_minutes,
    }

    if force and tp.exists():
        old = json.loads(tp.read_text())
        token["forced_from"] = old.get("actor", "unknown")

    tp.write_text(json.dumps(token, indent=2) + "\n")

    emit(
        Event(
            event_type="write_token_acquired",
            actor=actor,
            session_id=session_id,
            data={"lease_minutes": lease_minutes, "forced": force},
        ),
        root,
    )

    return {"acquired": True, **token}


def release(session_id: str, workspace: Path | None = None) -> dict:
    """Release the write token."""
    root = workspace or Path.cwd()
    tp = _token_path(root)

    if not tp.exists():
        return {"released": False, "reason": "no_token"}

    existing = json.loads(tp.read_text())
    if existing["session_id"] != session_id:
        return {
            "released": False,
            "reason": "not_holder",
            "holder": existing["actor"],
        }

    tp.unlink()

    emit(
        Event(
            event_type="write_token_released",
            actor=existing["actor"],
            session_id=session_id,
        ),
        root,
    )

    return {"released": True, "held_by": existing["actor"]}


def status(workspace: Path | None = None) -> dict:
    """Check the current write token status."""
    root = workspace or Path.cwd()
    tp = _token_path(root)

    if not tp.exists():
        return {"held": False}

    token = json.loads(tp.read_text())
    expires = _parse_ts(token["expires_at"])
    now = datetime.now(UTC)

    if now >= expires:
        return {
            "held": False,
            "expired": True,
            "last_holder": token["actor"],
            "expired_at": token["expires_at"],
        }

    remaining = (expires - now).total_seconds()
    return {
        "held": True,
        "actor": token["actor"],
        "session_id": token["session_id"],
        "acquired_at": token["acquired_at"],
        "expires_at": token["expires_at"],
        "remaining_seconds": int(remaining),
    }


def _compute_expiry(lease_minutes: int) -> str:
    """Compute an expiry timestamp from now."""
    from datetime import timedelta

    return (datetime.now(UTC) + timedelta(minutes=lease_minutes)).isoformat()
