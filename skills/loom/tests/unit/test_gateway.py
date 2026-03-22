"""Tests for the HTTP/SSE gateway."""

import json
from pathlib import Path

import pytest

from loom.memory import MemoryStore
from loom.models import MemoryEntry, MemoryType


def _init_workspace(tmp_path: Path) -> Path:
    """Create a workspace with some memory entries."""
    (tmp_path / ".loom").mkdir()
    store = MemoryStore(tmp_path)
    store.write(
        MemoryEntry(
            content="Use FastAPI for the backend",
            type=MemoryType.DECISION,
            rationale="Async-native",
        )
    )
    store.write(MemoryEntry(content="Complete auth migration", type=MemoryType.GOAL))
    store.close()

    # Initialize events.jsonl
    from loom.events import emit
    from loom.models import Event

    emit(Event(event_type="workspace_initialized", data={"project_type": "python"}), tmp_path)
    return tmp_path


@pytest.fixture
def app(tmp_path):
    """Create a gateway app with test workspace."""
    ws = _init_workspace(tmp_path)
    from loom.gateway import create_app

    return create_app(ws)


@pytest.fixture
def client(app):
    """Create a test client."""
    from starlette.testclient import TestClient

    return TestClient(app)


def test_health(client):
    """Health endpoint should always return 200."""
    r = client.get("/health")
    assert r.status_code == 200
    assert r.json()["status"] == "ok"


def test_search_memory(client):
    """REST search endpoint should return results."""
    r = client.post("/api/search", json={"query": "FastAPI"})
    assert r.status_code == 200
    data = r.json()
    assert len(data) >= 1
    assert "FastAPI" in data[0]["content"]


def test_log_decision(client):
    """REST log decision endpoint should create entry."""
    r = client.post(
        "/api/log-decision",
        json={"decision": "Use PostgreSQL", "rationale": "ACID compliance"},
    )
    assert r.status_code == 200
    data = r.json()
    assert data["status"] == "logged"
    assert "id" in data


def test_handoff_summary(client):
    """REST handoff endpoint should return structured summary."""
    r = client.get("/api/handoff")
    assert r.status_code == 200
    data = r.json()
    assert "current_goals" in data
    assert "recent_decisions" in data


def test_context(client):
    """REST context endpoint should return project context."""
    r = client.get("/api/context")
    assert r.status_code == 200
    data = r.json()
    assert "memory_entries" in data


def test_write_memory(client):
    """REST write memory endpoint should create entry."""
    r = client.post(
        "/api/write-memory",
        json={"content": "API uses cursor-based pagination", "type": "observation"},
    )
    assert r.status_code == 200
    assert r.json()["status"] == "written"


def test_auth_required_when_key_set(tmp_path, monkeypatch):
    """When LOOM_API_KEY is set, requests without it should get 401."""
    ws = _init_workspace(tmp_path)
    monkeypatch.setenv("LOOM_API_KEY", "test-secret-key")

    from starlette.testclient import TestClient

    from loom.gateway import create_app

    app = create_app(ws)
    client = TestClient(app)

    # No auth header → 401
    r = client.get("/api/context")
    assert r.status_code == 401

    # Wrong key → 401
    r = client.get("/api/context", headers={"Authorization": "Bearer wrong-key"})
    assert r.status_code == 401

    # Correct key → 200
    r = client.get(
        "/api/context",
        headers={"Authorization": "Bearer test-secret-key"},
    )
    assert r.status_code == 200


def test_health_no_auth_needed(tmp_path, monkeypatch):
    """Health endpoint should work even when auth is required."""
    ws = _init_workspace(tmp_path)
    monkeypatch.setenv("LOOM_API_KEY", "test-secret-key")

    from starlette.testclient import TestClient

    from loom.gateway import create_app

    app = create_app(ws)
    client = TestClient(app)

    r = client.get("/health")
    assert r.status_code == 200


def test_mcp_messages_tools_list(client):
    """MCP messages endpoint should list tools."""
    r = client.post(
        "/mcp/messages",
        json={"jsonrpc": "2.0", "id": 1, "method": "tools/list", "params": {}},
    )
    assert r.status_code == 200
    data = r.json()
    tools = data["result"]["tools"]
    tool_names = [t["name"] for t in tools]
    assert "loom_search_memory" in tool_names
    assert "loom_log_decision" in tool_names


def test_mcp_messages_tool_call(client):
    """MCP messages endpoint should execute tool calls."""
    r = client.post(
        "/mcp/messages",
        json={
            "jsonrpc": "2.0",
            "id": 2,
            "method": "tools/call",
            "params": {
                "name": "loom_search_memory",
                "arguments": {"query": "FastAPI"},
            },
        },
    )
    assert r.status_code == 200
    data = r.json()
    content = json.loads(data["result"]["content"][0]["text"])
    assert len(content) >= 1
