"""Workspace state inspection and inventory."""

from __future__ import annotations

import os
import subprocess
from pathlib import Path

from loom.constants import loom_dir
from loom.events import count as event_count
from loom.events import tail
from loom.memory import MemoryStore
from loom.runtime import compute_identity, load_identity


def get_workspace_state(workspace: Path | None = None) -> dict:
    """Return a concise operational snapshot of the workspace."""
    root = workspace or Path.cwd()
    loom = loom_dir(root)

    state = {
        "workspace": str(root),
        "loom_initialized": loom.exists(),
        "project_type": None,
        "runtime_identity": None,
        "identity_drift": None,
        "memory_entries": 0,
        "event_count": 0,
        "recent_events": [],
        "git_branch": None,
        "git_dirty": None,
        "file_count": 0,
    }

    if not loom.exists():
        return state

    # Runtime identity
    stored = load_identity(root)
    if stored:
        state["project_type"] = stored.project_type
        state["runtime_identity"] = stored.identity_hash
        # Check for drift
        live = compute_identity(root)
        if live.identity_hash == stored.identity_hash:
            state["identity_drift"] = "none"
        else:
            state["identity_drift"] = "detected"

    # Memory
    try:
        store = MemoryStore(root)
        state["memory_entries"] = store.count()
        store.close()
    except Exception:
        pass

    # Events
    state["event_count"] = event_count(root)
    state["recent_events"] = tail(5, root)

    # Git
    try:
        branch = subprocess.run(
            ["git", "rev-parse", "--abbrev-ref", "HEAD"], capture_output=True, text=True, cwd=root
        )
        if branch.returncode == 0:
            state["git_branch"] = branch.stdout.strip()

        dirty = subprocess.run(
            ["git", "status", "--porcelain"], capture_output=True, text=True, cwd=root
        )
        if dirty.returncode == 0:
            state["git_dirty"] = len(dirty.stdout.strip().splitlines()) > 0
    except FileNotFoundError:
        pass

    # File count (rough)
    try:
        count = 0
        for _, _, files in os.walk(root):
            count += len(files)
        state["file_count"] = count
    except Exception:
        pass

    return state


def doctor_check(workspace: Path | None = None) -> dict:
    """Run health checks and return structured diagnostics."""
    root = workspace or Path.cwd()
    loom = loom_dir(root)

    checks = []

    def check(name: str, ok: bool, detail: str = "", optional: bool = False):
        """Append a health check result."""
        checks.append({"name": name, "ok": ok, "detail": detail, "optional": optional})

    # .loom/ exists
    check(
        ".loom/ directory", loom.exists(), str(loom) if loom.exists() else "Run `loom init` first"
    )

    # runtime.json
    rt = loom / "runtime.json"
    check(
        "Runtime manifest", rt.exists(), "Present" if rt.exists() else "Missing — run `loom init`"
    )

    # memory.db
    mem = loom / "memory.db"
    check(
        "Memory database",
        mem.exists(),
        f"{mem.stat().st_size} bytes" if mem.exists() else "Missing",
    )

    # events.jsonl
    ev = loom / "events.jsonl"
    check("Event log", ev.exists(), f"{event_count(root)} events" if ev.exists() else "Missing")

    # Identity drift
    stored = load_identity(root)
    if stored:
        live = compute_identity(root)
        drift = live.identity_hash == stored.identity_hash
        check(
            "Runtime identity",
            drift,
            "No drift"
            if drift
            else f"DRIFT: stored={stored.identity_hash}, live={live.identity_hash}",
        )
    else:
        check("Runtime identity", False, "No stored identity")

    # Git (optional)
    try:
        r = subprocess.run(["git", "status"], capture_output=True, cwd=root)
        check(
            "Git repository",
            r.returncode == 0,
            "Clean" if r.returncode == 0 else "Not a git repo",
            optional=True,
        )
    except FileNotFoundError:
        check("Git repository", False, "Git not installed", optional=True)

    # Docker (optional)
    try:
        r = subprocess.run(["docker", "info"], capture_output=True)
        check(
            "Docker",
            r.returncode == 0,
            "Running" if r.returncode == 0 else "Not running",
            optional=True,
        )
    except FileNotFoundError:
        check("Docker", False, "Not installed", optional=True)

    required = [c for c in checks if not c.get("optional")]
    healthy = all(c["ok"] for c in required)
    required_pass = sum(c["ok"] for c in required)
    optional_pass = sum(c["ok"] for c in checks if c.get("optional"))
    optional_total = sum(1 for c in checks if c.get("optional"))

    summary = f"{required_pass}/{len(required)} required checks passed"
    if optional_total > 0:
        summary += f", {optional_pass}/{optional_total} optional"

    return {
        "healthy": healthy,
        "checks": checks,
        "summary": summary,
    }
