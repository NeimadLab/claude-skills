"""Import and export project memory from/to CLAUDE.md, .cursorrules, and markdown."""

from __future__ import annotations

import json
import re
from pathlib import Path

from loom.events import emit
from loom.memory import MemoryStore
from loom.models import Event, MemoryEntry, MemoryStatus, MemoryType


def _guess_type_from_content(text: str) -> MemoryType:
    """Heuristic: guess memory type from content."""
    lower = text.lower()
    if any(w in lower for w in ["decide", "chose", "use ", "adopt", "switch to", "prefer"]):
        return MemoryType.DECISION
    if any(w in lower for w in ["goal", "objective", "milestone", "by friday", "by end of"]):
        return MemoryType.GOAL
    if any(w in lower for w in ["risk", "danger", "concern", "warning", "not yet", "missing"]):
        return MemoryType.RISK
    if any(w in lower for w in ["convention", "always ", "never ", "prefer ", "style"]):
        return MemoryType.OBSERVATION
    return MemoryType.NOTE


def import_claude_md(file_path: Path, workspace: Path | None = None) -> dict:
    """Import a CLAUDE.md file into Loom memory.

    Parses markdown headings as categories. Each bullet point or paragraph
    becomes a memory entry. Instructions and decisions are imported as
    validated (trusted human-written content).
    """
    root = workspace or Path.cwd()
    text = file_path.read_text(encoding="utf-8")
    store = MemoryStore(root)

    entries = []
    current_section = "general"

    for line in text.splitlines():
        stripped = line.strip()

        # Track section headings
        if stripped.startswith("#"):
            current_section = stripped.lstrip("#").strip().lower()
            continue

        # Skip empty lines and decorators
        if not stripped or stripped.startswith("---") or stripped.startswith("```"):
            continue

        # Clean bullet prefix
        content = re.sub(r"^[-*+]\s+", "", stripped)
        if len(content) < 10:  # skip very short lines
            continue

        entry_type = _guess_type_from_content(content)
        tags = [current_section] if current_section != "general" else []

        entry = MemoryEntry(
            type=entry_type,
            status=MemoryStatus.VALIDATED,  # imported = trusted
            content=content,
            actor="import:claude-md",
            tags=tags,
        )
        store.write(entry)
        entries.append(entry.to_dict())

    store.close()

    emit(
        Event(
            event_type="memory_imported",
            actor="cli",
            data={"source": str(file_path), "format": "claude-md", "entries": len(entries)},
        ),
        root,
    )

    return {"source": str(file_path), "format": "claude-md", "imported": len(entries)}


def import_cursorrules(file_path: Path, workspace: Path | None = None) -> dict:
    """Import a .cursorrules file into Loom memory.

    Handles both JSON format and plain text format.
    """
    root = workspace or Path.cwd()
    text = file_path.read_text(encoding="utf-8")
    store = MemoryStore(root)
    entries = []

    # Try JSON first
    try:
        data = json.loads(text)
        rules = data if isinstance(data, list) else data.get("rules", [data])
        for rule in rules:
            content = rule if isinstance(rule, str) else json.dumps(rule)
            entry = MemoryEntry(
                type=MemoryType.OBSERVATION,
                status=MemoryStatus.VALIDATED,
                content=content,
                actor="import:cursorrules",
                tags=["cursor", "convention"],
            )
            store.write(entry)
            entries.append(entry.to_dict())
    except (json.JSONDecodeError, TypeError):
        # Plain text: treat each non-empty line as a rule
        for line in text.splitlines():
            stripped = line.strip()
            if not stripped or stripped.startswith("#") or len(stripped) < 10:
                continue
            content = re.sub(r"^[-*+]\s+", "", stripped)
            entry = MemoryEntry(
                type=_guess_type_from_content(content),
                status=MemoryStatus.VALIDATED,
                content=content,
                actor="import:cursorrules",
                tags=["cursor", "convention"],
            )
            store.write(entry)
            entries.append(entry.to_dict())

    store.close()

    emit(
        Event(
            event_type="memory_imported",
            actor="cli",
            data={"source": str(file_path), "format": "cursorrules", "entries": len(entries)},
        ),
        root,
    )

    return {"source": str(file_path), "format": "cursorrules", "imported": len(entries)}


def import_file(file_path: Path, workspace: Path | None = None) -> dict:
    """Auto-detect and import a file into Loom memory."""
    name = file_path.name.lower()

    if "claude" in name and name.endswith(".md"):
        return import_claude_md(file_path, workspace)
    elif "cursorrules" in name:
        return import_cursorrules(file_path, workspace)
    elif name.endswith(".md"):
        return import_claude_md(file_path, workspace)  # generic markdown
    else:
        return import_cursorrules(file_path, workspace)  # try as rules


def export_claude_md(workspace: Path | None = None, output: Path | None = None) -> str:
    """Export Loom memory as a CLAUDE.md file.

    Groups entries by type. Only includes validated and hypothesis entries.
    """
    root = workspace or Path.cwd()
    store = MemoryStore(root)

    sections = {
        "decisions": store.search("", type_filter="decision", status_filter="validated", limit=100),
        "goals": store.search("", type_filter="goal", limit=50),
        "risks": store.search("", type_filter="risk", limit=50),
        "conventions": store.search(
            "", type_filter="observation", status_filter="validated", limit=100
        ),
        "notes": store.search("", type_filter="note", status_filter="validated", limit=50),
    }
    store.close()

    lines = ["# Project Memory (exported from Loom)", ""]

    for section_name, entries in sections.items():
        if not entries:
            continue
        lines.append(f"## {section_name.title()}")
        lines.append("")
        for entry in entries:
            status_tag = f" ({entry['status']})" if entry["status"] != "validated" else ""
            lines.append(f"- {entry['content']}{status_tag}")
            if entry.get("rationale"):
                lines.append(f"  - Rationale: {entry['rationale']}")
        lines.append("")

    content = "\n".join(lines)

    if output:
        output.write_text(content, encoding="utf-8")
    else:
        dest = root / "CLAUDE.md"
        dest.write_text(content, encoding="utf-8")

    emit(
        Event(
            event_type="memory_exported",
            actor="cli",
            data={
                "format": "claude-md",
                "entries": sum(len(v) for v in sections.values()),
            },
        ),
        root,
    )

    return content


def export_markdown(workspace: Path | None = None, output: Path | None = None) -> str:
    """Export full Loom memory as readable markdown."""
    root = workspace or Path.cwd()
    store = MemoryStore(root)
    all_entries = store.recent(500)
    store.close()

    lines = ["# Loom Memory Export", "", f"Total entries: {len(all_entries)}", ""]

    for entry in all_entries:
        lines.append(f"### [{entry['type']}] {entry['content'][:80]}")
        lines.append(f"- **Status:** {entry['status']}")
        lines.append(f"- **Actor:** {entry.get('actor', 'unknown')}")
        lines.append(f"- **Date:** {entry['timestamp'][:10]}")
        if entry.get("rationale"):
            lines.append(f"- **Rationale:** {entry['rationale']}")
        tags = entry.get("tags", "[]")
        if tags and tags != "[]":
            lines.append(f"- **Tags:** {tags}")
        lines.append("")

    content = "\n".join(lines)

    if output:
        output.write_text(content, encoding="utf-8")

    return content
