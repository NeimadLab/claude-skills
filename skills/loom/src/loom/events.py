"""Append-only JSONL event log."""

from __future__ import annotations

from typing import TYPE_CHECKING

from loom.constants import EVENTS_FILE, loom_dir

if TYPE_CHECKING:
    from pathlib import Path

    from loom.models import Event


def _events_path(workspace: Path | None = None) -> Path:
    return loom_dir(workspace) / EVENTS_FILE


def emit(event: Event, workspace: Path | None = None) -> None:
    """Append an event to the log."""
    path = _events_path(workspace)
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "a") as f:
        f.write(event.to_json() + "\n")


def tail(n: int = 20, workspace: Path | None = None) -> list[dict]:
    """Read the last N events."""
    import json

    path = _events_path(workspace)
    if not path.exists():
        return []
    lines = path.read_text().strip().splitlines()
    return [json.loads(line) for line in lines[-n:]]


def count(workspace: Path | None = None) -> int:
    """Count total events."""
    path = _events_path(workspace)
    if not path.exists():
        return 0
    return sum(1 for _ in open(path))
