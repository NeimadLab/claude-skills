"""Session and actor management.

Tracks which AI tool (actor) is working on a workspace, when sessions
start and end, and links memory entries to sessions for full auditability.
"""

from __future__ import annotations

import sqlite3
from datetime import UTC, datetime
from pathlib import Path

from loom.constants import loom_dir
from loom.events import emit
from loom.models import Event, generate_id

SESSION_SCHEMA = """
CREATE TABLE IF NOT EXISTS sessions (
    id          TEXT PRIMARY KEY,
    actor       TEXT NOT NULL,
    model_name  TEXT,
    started_at  TEXT NOT NULL,
    ended_at    TEXT,
    status      TEXT NOT NULL DEFAULT 'active',
    summary     TEXT
);
"""


class SessionStore:
    """Manage sessions in the workspace database."""

    def __init__(self, workspace: Path | None = None):
        """Open or create the sessions table in the memory database."""
        root = workspace or Path.cwd()
        db_path = loom_dir(root) / "memory.db"
        self.workspace = root
        self.conn = sqlite3.connect(str(db_path), check_same_thread=False)
        self.conn.row_factory = sqlite3.Row
        self.conn.execute("PRAGMA journal_mode=WAL")
        self.conn.execute(SESSION_SCHEMA)
        self.conn.commit()

    def open_session(
        self,
        actor: str,
        model_name: str | None = None,
    ) -> dict:
        """Open a new session. Returns session record."""
        session_id = generate_id()
        now = datetime.now(UTC).isoformat()

        self.conn.execute(
            "INSERT INTO sessions (id, actor, model_name, started_at, status) "
            "VALUES (?, ?, ?, ?, 'active')",
            (session_id, actor, model_name, now),
        )
        self.conn.commit()

        emit(
            Event(
                event_type="session_opened",
                actor=actor,
                session_id=session_id,
                data={"model_name": model_name},
            ),
            self.workspace,
        )

        return {
            "id": session_id,
            "actor": actor,
            "model_name": model_name,
            "started_at": now,
            "status": "active",
        }

    def close_session(self, session_id: str, summary: str | None = None) -> dict:
        """Close an active session."""
        now = datetime.now(UTC).isoformat()
        row = self.conn.execute("SELECT * FROM sessions WHERE id = ?", (session_id,)).fetchone()

        if not row:
            return {"error": f"Session not found: {session_id}"}
        if row["status"] != "active":
            return {"error": f"Session already {row['status']}"}

        self.conn.execute(
            "UPDATE sessions SET status = 'closed', ended_at = ?, summary = ? WHERE id = ?",
            (now, summary, session_id),
        )
        self.conn.commit()

        emit(
            Event(
                event_type="session_closed",
                actor=row["actor"],
                session_id=session_id,
                data={"summary": summary, "duration_seconds": _duration(row["started_at"], now)},
            ),
            self.workspace,
        )

        return {
            "id": session_id,
            "status": "closed",
            "ended_at": now,
            "summary": summary,
        }

    def get_active(self) -> dict | None:
        """Get the currently active session, if any."""
        row = self.conn.execute(
            "SELECT * FROM sessions WHERE status = 'active' ORDER BY started_at DESC LIMIT 1"
        ).fetchone()
        return dict(row) if row else None

    def get(self, session_id: str) -> dict | None:
        """Get a session by ID."""
        row = self.conn.execute("SELECT * FROM sessions WHERE id = ?", (session_id,)).fetchone()
        return dict(row) if row else None

    def list_sessions(self, limit: int = 20) -> list[dict]:
        """List recent sessions, newest first."""
        rows = self.conn.execute(
            "SELECT * FROM sessions ORDER BY started_at DESC LIMIT ?",
            (limit,),
        ).fetchall()
        return [dict(r) for r in rows]

    def cleanup_stale(self, max_age_hours: int = 24) -> int:
        """Close sessions that have been active for too long."""
        now = datetime.now(UTC)
        rows = self.conn.execute(
            "SELECT id, started_at, actor FROM sessions WHERE status = 'active'"
        ).fetchall()

        closed = 0
        for row in rows:
            started = datetime.fromisoformat(row["started_at"])
            age_hours = (now - started).total_seconds() / 3600
            if age_hours > max_age_hours:
                self.close_session(
                    row["id"],
                    summary=f"Auto-closed after {age_hours:.0f}h (stale)",
                )
                closed += 1

        return closed

    def close(self):
        """Close the database connection."""
        self.conn.close()


def _duration(start_iso: str, end_iso: str) -> int:
    """Calculate duration in seconds between two ISO timestamps."""
    start = datetime.fromisoformat(start_iso)
    end = datetime.fromisoformat(end_iso)
    return int((end - start).total_seconds())
