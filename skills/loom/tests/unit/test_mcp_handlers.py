"""Tests for MCP server handlers (testable without transport)."""

import pytest

from loom.mcp_server import (
    handle_get_context,
    handle_get_handoff_summary,
    handle_log_decision,
    handle_search_memory,
    handle_write_memory,
)
from loom.memory import MemoryStore
from loom.models import MemoryEntry, MemoryType
from loom.runtime import compute_identity, save_identity


@pytest.fixture
def workspace(tmp_path):
    """Create a workspace with .loom/ and some memory entries."""
    loom_dir = tmp_path / ".loom"
    loom_dir.mkdir()
    # Create runtime manifest
    identity = compute_identity(tmp_path)
    save_identity(identity, tmp_path)
    # Populate memory
    store = MemoryStore(tmp_path)
    store.write(
        MemoryEntry(content="Use FastAPI for backend", type=MemoryType.DECISION, rationale="Async")
    )
    store.write(MemoryEntry(content="Migrate to PostgreSQL", type=MemoryType.GOAL))
    store.write(MemoryEntry(content="No rate limiting", type=MemoryType.RISK))
    store.write(MemoryEntry(content="Team prefers explicit errors", type=MemoryType.OBSERVATION))
    store.close()
    return tmp_path


def test_handle_search_memory(workspace):
    store = MemoryStore(workspace)
    results = handle_search_memory(store, {"query": "FastAPI"})
    assert len(results) >= 1
    assert "FastAPI" in results[0]["content"]
    store.close()


def test_handle_search_empty(workspace):
    store = MemoryStore(workspace)
    results = handle_search_memory(store, {"query": "", "type": "decision"})
    assert len(results) >= 1
    store.close()


def test_handle_write_memory(workspace):
    store = MemoryStore(workspace)
    result = handle_write_memory(store, {"content": "New note", "type": "note"}, workspace)
    assert result["status"] == "written"
    assert "id" in result
    # Verify it was stored
    found = store.get(result["id"])
    assert found is not None
    assert found["content"] == "New note"
    store.close()


def test_handle_log_decision(workspace):
    store = MemoryStore(workspace)
    result = handle_log_decision(
        store, {"decision": "Use Redis", "rationale": "Fast caching"}, workspace
    )
    assert result["status"] == "logged"
    found = store.get(result["id"])
    assert found["type"] == "decision"
    assert found["rationale"] == "Fast caching"
    store.close()


def test_handle_get_handoff_summary(workspace):
    store = MemoryStore(workspace)
    summary = handle_get_handoff_summary(store, {"depth": "compact"})
    assert "current_goals" in summary
    assert "recent_decisions" in summary
    assert "open_risks" in summary
    assert len(summary["current_goals"]) >= 1
    assert len(summary["open_risks"]) >= 1
    store.close()


def test_handle_get_context(workspace):
    store = MemoryStore(workspace)
    ctx = handle_get_context(store, workspace)
    assert "project_type" in ctx
    assert "memory_entries" in ctx
    assert ctx["memory_entries"] >= 4
    assert len(ctx["recent_decisions"]) >= 1
    store.close()
