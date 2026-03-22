"""Tests for session management."""

from pathlib import Path

from loom.sessions import SessionStore


def _init(tmp_path: Path) -> Path:
    (tmp_path / ".loom").mkdir()
    return tmp_path


def test_open_session(tmp_path):
    ws = _init(tmp_path)
    store = SessionStore(ws)
    result = store.open_session("claude-code", "claude-opus-4")
    store.close()

    assert result["actor"] == "claude-code"
    assert result["model_name"] == "claude-opus-4"
    assert result["status"] == "active"
    assert "id" in result


def test_close_session(tmp_path):
    ws = _init(tmp_path)
    store = SessionStore(ws)
    opened = store.open_session("cursor", "gpt-4o")
    result = store.close_session(opened["id"], "Completed auth migration")
    store.close()

    assert result["status"] == "closed"
    assert result["summary"] == "Completed auth migration"


def test_get_active_session(tmp_path):
    ws = _init(tmp_path)
    store = SessionStore(ws)
    store.open_session("claude-code")

    active = store.get_active()
    assert active is not None
    assert active["actor"] == "claude-code"
    assert active["status"] == "active"
    store.close()


def test_get_active_returns_none_when_closed(tmp_path):
    ws = _init(tmp_path)
    store = SessionStore(ws)
    opened = store.open_session("cursor")
    store.close_session(opened["id"])

    active = store.get_active()
    assert active is None
    store.close()


def test_list_sessions(tmp_path):
    ws = _init(tmp_path)
    store = SessionStore(ws)
    store.open_session("claude-code", "claude-opus-4")
    store.open_session("cursor", "gpt-4o")

    sessions = store.list_sessions()
    assert len(sessions) == 2
    # Most recent first
    assert sessions[0]["actor"] == "cursor"
    store.close()


def test_close_nonexistent_session(tmp_path):
    ws = _init(tmp_path)
    store = SessionStore(ws)
    result = store.close_session("fake-id")
    store.close()

    assert "error" in result


def test_double_close(tmp_path):
    ws = _init(tmp_path)
    store = SessionStore(ws)
    opened = store.open_session("claude-code")
    store.close_session(opened["id"])

    result = store.close_session(opened["id"])
    assert "error" in result
    store.close()


def test_session_persists_across_connections(tmp_path):
    ws = _init(tmp_path)

    store1 = SessionStore(ws)
    store1.open_session("claude-code")
    store1.close()

    store2 = SessionStore(ws)
    sessions = store2.list_sessions()
    assert len(sessions) == 1
    assert sessions[0]["actor"] == "claude-code"
    store2.close()
