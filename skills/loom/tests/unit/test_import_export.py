"""Tests for import/export functionality."""

from pathlib import Path

from loom.import_export import (
    export_claude_md,
    export_markdown,
    import_claude_md,
    import_cursorrules,
    import_file,
)
from loom.memory import MemoryStore
from loom.models import MemoryEntry, MemoryStatus, MemoryType


def _init_workspace(tmp_path: Path) -> Path:
    """Create a minimal workspace."""
    (tmp_path / ".loom").mkdir()
    return tmp_path


def test_import_claude_md(tmp_path):
    ws = _init_workspace(tmp_path)
    md = tmp_path / "CLAUDE.md"
    md.write_text(
        "# Project Instructions\n\n"
        "- Use PostgreSQL for the database\n"
        "- Always write tests before implementation\n"
        "- Risk: no rate limiting on the API yet\n\n"
        "## Goals\n\n"
        "- Complete the auth migration by Friday\n"
    )

    result = import_claude_md(md, ws)
    assert result["imported"] >= 3

    store = MemoryStore(ws)
    assert store.count() >= 3
    # Imported entries should be validated (human-written = trusted)
    entries = store.search("PostgreSQL")
    assert len(entries) >= 1
    assert entries[0]["status"] == "validated"
    store.close()


def test_import_cursorrules_json(tmp_path):
    ws = _init_workspace(tmp_path)
    rules = tmp_path / ".cursorrules"
    rules.write_text(
        '{"rules": ["Always use TypeScript strict mode", '
        '"Prefer functional components over class components"]}'
    )

    result = import_cursorrules(rules, ws)
    assert result["imported"] == 2

    store = MemoryStore(ws)
    entries = store.search("TypeScript")
    assert len(entries) >= 1
    store.close()


def test_import_cursorrules_plain_text(tmp_path):
    ws = _init_workspace(tmp_path)
    rules = tmp_path / ".cursorrules"
    rules.write_text(
        "# Cursor Rules\n"
        "Always use explicit return types in TypeScript\n"
        "Prefer composition over inheritance for components\n"
        "Short lines are fine\n"  # <10 chars after strip — should be skipped
    )

    result = import_cursorrules(rules, ws)
    assert result["imported"] == 3  # header skipped, all others imported


def test_import_file_auto_detect(tmp_path):
    ws = _init_workspace(tmp_path)
    md = tmp_path / "CLAUDE.md"
    md.write_text("- Use FastAPI for the backend\n")

    result = import_file(md, ws)
    assert result["format"] == "claude-md"


def test_export_claude_md(tmp_path):
    ws = _init_workspace(tmp_path)
    store = MemoryStore(ws)
    store.write(
        MemoryEntry(
            content="Use JWT for authentication",
            type=MemoryType.DECISION,
            status=MemoryStatus.VALIDATED,
            rationale="Stateless and scalable",
        )
    )
    store.write(
        MemoryEntry(
            content="Migrate to PostgreSQL",
            type=MemoryType.GOAL,
        )
    )
    store.close()

    out = tmp_path / "output.md"
    content = export_claude_md(ws, out)

    assert "JWT" in content
    assert "## Decisions" in content
    assert out.exists()


def test_export_markdown(tmp_path):
    ws = _init_workspace(tmp_path)
    store = MemoryStore(ws)
    store.write(MemoryEntry(content="Test entry", type=MemoryType.NOTE))
    store.close()

    content = export_markdown(ws)
    assert "Test entry" in content
    assert "Loom Memory Export" in content


def test_roundtrip_import_export(tmp_path):
    """Import → populate memory → export → verify content survives."""
    ws = _init_workspace(tmp_path)

    # Write a CLAUDE.md
    md = tmp_path / "source.md"
    md.write_text(
        "# Decisions\n\n"
        "- Use Redis for session caching because of low latency\n"
        "- Adopt conventional commits for all repositories\n"
    )

    # Import
    import_claude_md(md, ws)

    # Export
    out = tmp_path / "exported.md"
    content = export_claude_md(ws, out)

    assert "Redis" in content
    assert "conventional commits" in content
