"""Data models for Loom entities."""

from __future__ import annotations

import json
import time
from dataclasses import asdict, dataclass, field
from enum import StrEnum
from typing import Any


def generate_id() -> str:
    """Generate a ULID-like sortable unique ID."""
    import os

    ts = int(time.time() * 1000)
    rand = os.urandom(10).hex()
    return f"{ts:013x}{rand[:16]}"


class MemoryType(StrEnum):
    DECISION = "decision"
    ARTIFACT = "artifact"
    GOAL = "goal"
    RISK = "risk"
    NOTE = "note"
    OBSERVATION = "observation"


class MemoryStatus(StrEnum):
    HYPOTHESIS = "hypothesis"
    VALIDATED = "validated"
    OBSOLETE = "obsolete"
    REJECTED = "rejected"


VALID_TRANSITIONS = {
    MemoryStatus.HYPOTHESIS: {MemoryStatus.VALIDATED, MemoryStatus.REJECTED},
    MemoryStatus.VALIDATED: {MemoryStatus.OBSOLETE},
    MemoryStatus.OBSOLETE: set(),
    MemoryStatus.REJECTED: set(),
}


@dataclass
class MemoryEntry:
    id: str = field(default_factory=generate_id)
    type: MemoryType = MemoryType.NOTE
    status: MemoryStatus = MemoryStatus.HYPOTHESIS
    content: str = ""
    rationale: str | None = None
    actor: str | None = None
    session_id: str | None = None
    timestamp: str = field(
        default_factory=lambda: time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
    )
    linked_files: list[str] = field(default_factory=list)
    linked_commits: list[str] = field(default_factory=list)
    tags: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        """Convert to a plain dictionary with enum values as strings."""
        d = asdict(self)
        d["type"] = self.type.value
        d["status"] = self.status.value
        return d


@dataclass
class Event:
    event_type: str
    timestamp: str = field(
        default_factory=lambda: time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
    )
    actor: str | None = None
    session_id: str | None = None
    data: dict[str, Any] = field(default_factory=dict)

    def to_json(self) -> str:
        """Serialize to a compact JSON string for the event log."""
        return json.dumps(asdict(self), separators=(",", ":"))


@dataclass
class RuntimeIdentity:
    project_type: str
    lockfile_hashes: dict[str, str]
    tool_versions: dict[str, str]
    identity_hash: str
    computed_at: str = field(
        default_factory=lambda: time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
    )
