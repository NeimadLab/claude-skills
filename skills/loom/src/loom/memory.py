"""SQLite-backed project memory with FTS5 full-text search."""

from __future__ import annotations

import json
import re
import sqlite3
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from pathlib import Path

    from loom.models import MemoryEntry

from loom.constants import MEMORY_DB, loom_dir

SCHEMA = """
CREATE TABLE IF NOT EXISTS memory (
    id              TEXT PRIMARY KEY,
    type            TEXT NOT NULL,
    status          TEXT NOT NULL DEFAULT 'hypothesis',
    content         TEXT NOT NULL,
    rationale       TEXT,
    actor           TEXT,
    session_id      TEXT,
    timestamp       TEXT NOT NULL,
    linked_files    TEXT DEFAULT '[]',
    linked_commits  TEXT DEFAULT '[]',
    tags            TEXT DEFAULT '[]'
);

CREATE VIRTUAL TABLE IF NOT EXISTS memory_fts USING fts5(
    content, tags, content=memory, content_rowid=rowid
);

CREATE TRIGGER IF NOT EXISTS memory_ai AFTER INSERT ON memory BEGIN
    INSERT INTO memory_fts(rowid, content, tags)
    VALUES (new.rowid, new.content, new.tags);
END;

CREATE TRIGGER IF NOT EXISTS memory_ad AFTER DELETE ON memory BEGIN
    INSERT INTO memory_fts(memory_fts, rowid, content, tags)
    VALUES ('delete', old.rowid, old.content, old.tags);
END;

CREATE TRIGGER IF NOT EXISTS memory_au AFTER UPDATE ON memory BEGIN
    INSERT INTO memory_fts(memory_fts, rowid, content, tags)
    VALUES ('delete', old.rowid, old.content, old.tags);
    INSERT INTO memory_fts(rowid, content, tags)
    VALUES (new.rowid, new.content, new.tags);
END;
"""

# FTS5 special characters that need escaping
_FTS5_SPECIAL = re.compile(r'[+\-*/~^(){}\[\]<>@#$%&|!?:;,."\x27=]')


def _sanitize_fts_query(query: str) -> str:
    """Sanitize a query string for FTS5 to prevent syntax errors.

    FTS5 treats characters like +, -, *, etc. as operators.
    This function wraps each word in double quotes to treat them as literals.
    """
    query = query.strip()
    if not query:
        return ""
    # If query contains special chars, quote each word
    words = query.split()
    safe_words = []
    for word in words:
        if _FTS5_SPECIAL.search(word):
            # Escape double quotes inside the word and wrap
            safe = word.replace('"', '""')
            safe_words.append(f'"{safe}"')
        else:
            safe_words.append(word)
    return " ".join(safe_words)


class MemoryStore:
    """SQLite-backed memory store with FTS5 search.

    Thread-safe: uses check_same_thread=False with WAL mode.
    """

    def __init__(self, workspace: Path | None = None):
        """Initialize the memory store, creating the database if needed."""
        self.db_path = loom_dir(workspace) / MEMORY_DB
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self.conn = sqlite3.connect(
            str(self.db_path),
            check_same_thread=False,  # FIX E3b: thread safety
        )
        self.conn.row_factory = sqlite3.Row
        self.conn.execute("PRAGMA journal_mode=WAL")
        self.conn.executescript(SCHEMA)

    def close(self) -> None:
        """Close the database connection."""
        self.conn.close()

    def write(self, entry: MemoryEntry) -> MemoryEntry:
        """Insert a memory entry into the store."""
        self.conn.execute(
            """INSERT INTO memory (id, type, status, content, rationale, actor,
               session_id, timestamp, linked_files, linked_commits, tags)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
            (
                entry.id,
                entry.type.value,
                entry.status.value,
                entry.content,
                entry.rationale,
                entry.actor,
                entry.session_id,
                entry.timestamp,
                json.dumps(entry.linked_files),
                json.dumps(entry.linked_commits),
                json.dumps(entry.tags),
            ),
        )
        self.conn.commit()
        return entry

    def search(
        self,
        query: str,
        limit: int = 10,
        type_filter: str | None = None,
        status_filter: str | None = None,
    ) -> list[dict]:
        """Full-text search with optional type and status filters.

        Handles special characters safely by sanitizing the FTS5 query.
        Falls back to LIKE search if FTS5 query is empty after sanitization.
        """
        sanitized = _sanitize_fts_query(query)

        if sanitized:
            sql = """
                SELECT m.* FROM memory m
                JOIN memory_fts f ON m.rowid = f.rowid
                WHERE memory_fts MATCH ?
            """
            params: list = [sanitized]
        else:
            sql = "SELECT * FROM memory m WHERE 1=1"
            params = []

        if type_filter:
            sql += " AND m.type = ?"
            params.append(type_filter)
        if status_filter:
            sql += " AND m.status = ?"
            params.append(status_filter)

        sql += " ORDER BY m.timestamp DESC LIMIT ?"
        params.append(limit)

        try:
            rows = self.conn.execute(sql, params).fetchall()
        except sqlite3.OperationalError:
            # Fallback: if FTS5 still fails, do a LIKE search
            sql = "SELECT * FROM memory m WHERE m.content LIKE ?"
            params = [f"%{query}%"]
            if type_filter:
                sql += " AND m.type = ?"
                params.append(type_filter)
            if status_filter:
                sql += " AND m.status = ?"
                params.append(status_filter)
            sql += " ORDER BY m.timestamp DESC LIMIT ?"
            params.append(limit)
            rows = self.conn.execute(sql, params).fetchall()

        return [dict(row) for row in rows]

    def get(self, entry_id: str) -> dict | None:
        """Get a single entry by its ID."""
        row = self.conn.execute("SELECT * FROM memory WHERE id = ?", (entry_id,)).fetchone()
        return dict(row) if row else None

    def update_status(self, entry_id: str, new_status: str, reason: str = "") -> bool:
        """Update the status of a memory entry with audit trail."""
        self.conn.execute(
            "UPDATE memory SET status = ? WHERE id = ?",
            (new_status, entry_id),
        )
        self.conn.commit()
        return self.conn.total_changes > 0

    def count(self) -> int:
        """Count total entries in the store."""
        return self.conn.execute("SELECT COUNT(*) FROM memory").fetchone()[0]

    def recent(self, n: int = 10) -> list[dict]:
        """Get the N most recent entries, ordered by timestamp descending."""
        rows = self.conn.execute(
            "SELECT * FROM memory ORDER BY timestamp DESC LIMIT ?", (n,)
        ).fetchall()
        return [dict(row) for row in rows]
