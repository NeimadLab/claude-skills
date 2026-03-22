"""Recovery, rebuild, and memory maintenance.

- Crash recovery: integrity checks, stale session cleanup
- State rebuild: reconstruct memory.db from events.jsonl
- Memory decay: auto-obsolete unvalidated entries past TTL
"""

from __future__ import annotations

import json
import sqlite3
from datetime import UTC, datetime, timedelta
from pathlib import Path

from loom.constants import loom_dir
from loom.events import emit
from loom.models import Event


def integrity_check(workspace: Path | None = None) -> dict:
    """Run integrity checks on the workspace. Returns a report.

    Checks:
    1. .loom/ directory exists
    2. memory.db is a valid SQLite database
    3. memory_fts table in sync with memory table
    4. events.jsonl is valid (each line parses as JSON)
    5. runtime.json is valid JSON
    6. No stale write tokens
    7. No stale sessions (active > 24h)
    """
    root = workspace or Path.cwd()
    ld = loom_dir(root)
    checks = []

    def check(name: str, ok: bool, detail: str = ""):
        checks.append({"name": name, "ok": ok, "detail": detail})

    # 1. .loom/ exists
    check(".loom/ directory", ld.exists(), str(ld) if ld.exists() else "Missing")

    if not ld.exists():
        return {"healthy": False, "checks": checks, "repaired": 0}

    # 2. memory.db valid
    db_path = ld / "memory.db"
    db_ok = False
    if db_path.exists():
        try:
            conn = sqlite3.connect(str(db_path))
            conn.execute("SELECT count(*) FROM memory")
            conn.close()
            db_ok = True
            check("memory.db", True, "Valid SQLite")
        except sqlite3.DatabaseError as e:
            check("memory.db", False, f"Corrupt: {e}")
    else:
        check("memory.db", False, "Missing")

    # 3. FTS5 sync
    if db_ok:
        try:
            conn = sqlite3.connect(str(db_path))
            mem_count = conn.execute("SELECT count(*) FROM memory").fetchone()[0]
            fts_count = conn.execute("SELECT count(*) FROM memory_fts").fetchone()[0]
            conn.close()
            in_sync = mem_count == fts_count
            check(
                "FTS5 index",
                in_sync,
                f"memory={mem_count}, fts={fts_count}" + ("" if in_sync else " — OUT OF SYNC"),
            )
        except sqlite3.DatabaseError:
            check("FTS5 index", False, "Error querying FTS5")

    # 4. events.jsonl valid
    events_path = ld / "events.jsonl"
    if events_path.exists():
        bad_lines = 0
        total_lines = 0
        for line in events_path.read_text().splitlines():
            if not line.strip():
                continue
            total_lines += 1
            try:
                json.loads(line)
            except json.JSONDecodeError:
                bad_lines += 1
        check(
            "events.jsonl",
            bad_lines == 0,
            f"{total_lines} events" + (f", {bad_lines} corrupt" if bad_lines else ""),
        )
    else:
        check("events.jsonl", True, "No events yet")

    # 5. runtime.json valid
    rt_path = ld / "runtime.json"
    if rt_path.exists():
        try:
            json.loads(rt_path.read_text())
            check("runtime.json", True, "Valid")
        except json.JSONDecodeError:
            check("runtime.json", False, "Invalid JSON")
    else:
        check("runtime.json", False, "Missing")

    # 6. Stale write token
    from loom import write_token

    token_status = write_token.status(root)
    if token_status.get("expired"):
        check("write_token", False, f"Expired token from {token_status.get('last_holder')}")
    else:
        check("write_token", True, "Held" if token_status.get("held") else "Free")

    # 7. Stale sessions
    if db_ok:
        from loom.sessions import SessionStore

        ss = SessionStore(root)
        active = ss.get_active()
        if active:
            started = datetime.fromisoformat(active["started_at"])
            age_h = (datetime.now(started.tzinfo or None) - started).total_seconds() / 3600
            if age_h > 24:
                check("sessions", False, f"Stale session from {active['actor']} ({age_h:.0f}h)")
            else:
                check("sessions", True, f"Active: {active['actor']} ({age_h:.0f}h)")
        else:
            check("sessions", True, "No active session")
        ss.close()

    healthy = all(c["ok"] for c in checks)
    return {"healthy": healthy, "checks": checks, "repaired": 0}


def repair(workspace: Path | None = None) -> dict:
    """Attempt automatic repairs on the workspace.

    Repairs:
    1. Clean up expired write tokens
    2. Close stale sessions
    3. Rebuild FTS5 index if out of sync
    """
    root = workspace or Path.cwd()
    repaired = 0
    details = []

    # 1. Expired write token
    from loom import write_token

    ts = write_token.status(root)
    if ts.get("expired"):
        tp = loom_dir(root) / "write_token.json"
        if tp.exists():
            tp.unlink()
            repaired += 1
            details.append("Removed expired write token")

    # 2. Stale sessions
    from loom.sessions import SessionStore

    try:
        ss = SessionStore(root)
        closed = ss.cleanup_stale(max_age_hours=24)
        if closed > 0:
            repaired += closed
            details.append(f"Closed {closed} stale session(s)")
        ss.close()
    except Exception:
        pass

    # 3. FTS5 rebuild
    db_path = loom_dir(root) / "memory.db"
    if db_path.exists():
        try:
            conn = sqlite3.connect(str(db_path))
            mem_count = conn.execute("SELECT count(*) FROM memory").fetchone()[0]
            fts_count = conn.execute("SELECT count(*) FROM memory_fts").fetchone()[0]
            if mem_count != fts_count:
                conn.execute("DELETE FROM memory_fts")
                conn.execute(
                    "INSERT INTO memory_fts(rowid, content, tags) "
                    "SELECT rowid, content, tags FROM memory"
                )
                conn.commit()
                repaired += 1
                details.append(f"Rebuilt FTS5 index ({mem_count} entries)")
            conn.close()
        except Exception:
            pass

    emit(
        Event(event_type="workspace_repaired", data={"repaired": repaired, "details": details}),
        root,
    )

    return {"repaired": repaired, "details": details}


def rebuild_from_events(workspace: Path | None = None) -> dict:
    """Reconstruct memory.db from events.jsonl.

    This is the nuclear option: when memory.db is corrupt but events.jsonl is intact.
    Replays all memory_written and decision_logged events to rebuild the database.
    """
    root = workspace or Path.cwd()
    events_path = loom_dir(root) / "events.jsonl"

    if not events_path.exists():
        return {"error": "No events.jsonl found", "rebuilt": 0}

    # Backup existing memory.db
    db_path = loom_dir(root) / "memory.db"
    if db_path.exists():
        backup = loom_dir(root) / "memory.db.backup"
        db_path.rename(backup)

    # Create fresh database
    from loom.memory import MemoryStore
    from loom.models import MemoryEntry, MemoryType

    store = MemoryStore(root)
    rebuilt = 0
    skipped = 0

    for line in events_path.read_text().splitlines():
        if not line.strip():
            continue
        try:
            event = json.loads(line)
        except json.JSONDecodeError:
            skipped += 1
            continue

        etype = event.get("event_type", "")
        data = event.get("data", {})

        if etype in ("memory_written", "decision_logged", "memory_imported"):
            content = data.get("decision", data.get("content"))
            if not content:
                skipped += 1
                continue

            entry_type = data.get("type", "decision" if etype == "decision_logged" else "note")
            try:
                entry = MemoryEntry(
                    type=MemoryType(entry_type),
                    content=content,
                    actor=event.get("actor"),
                    rationale=data.get("rationale"),
                )
                store.write(entry)
                rebuilt += 1
            except (ValueError, KeyError):
                skipped += 1

    store.close()

    emit(
        Event(
            event_type="memory_rebuilt",
            data={"rebuilt": rebuilt, "skipped": skipped},
        ),
        root,
    )

    return {"rebuilt": rebuilt, "skipped": skipped}


def decay_memories(
    workspace: Path | None = None,
    ttl_days: int = 30,
    dry_run: bool = False,
) -> dict:
    """Auto-obsolete unvalidated hypothesis entries older than TTL.

    Only affects entries with status='hypothesis'. Validated, obsolete,
    and rejected entries are never touched.
    """
    root = workspace or Path.cwd()
    db_path = loom_dir(root) / "memory.db"

    if not db_path.exists():
        return {"decayed": 0, "checked": 0}

    cutoff = (datetime.now(UTC) - timedelta(days=ttl_days)).isoformat()

    conn = sqlite3.connect(str(db_path), check_same_thread=False)
    conn.row_factory = sqlite3.Row

    # Find candidates
    candidates = conn.execute(
        "SELECT id, content, timestamp FROM memory WHERE status = 'hypothesis' AND timestamp < ?",
        (cutoff,),
    ).fetchall()

    if dry_run:
        conn.close()
        return {
            "decayed": 0,
            "would_decay": len(candidates),
            "checked": len(candidates),
            "dry_run": True,
            "entries": [{"id": r["id"], "content": r["content"][:60]} for r in candidates],
        }

    decayed = 0
    for row in candidates:
        conn.execute(
            "UPDATE memory SET status = 'obsolete' WHERE id = ?",
            (row["id"],),
        )
        decayed += 1

    conn.commit()
    conn.close()

    if decayed > 0:
        emit(
            Event(
                event_type="memory_decayed",
                data={"decayed": decayed, "ttl_days": ttl_days},
            ),
            root,
        )

    return {"decayed": decayed, "checked": len(candidates)}
