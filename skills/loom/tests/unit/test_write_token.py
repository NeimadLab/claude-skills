"""Tests for write token (lease-based single-writer exclusion)."""

import json
from pathlib import Path

from loom import write_token
from loom.constants import loom_dir


def _init(tmp_path: Path) -> Path:
    (tmp_path / ".loom").mkdir()
    return tmp_path


def test_acquire_token(tmp_path):
    ws = _init(tmp_path)
    result = write_token.acquire("session-1", "claude-code", ws)
    assert result["acquired"] is True
    assert result["actor"] == "claude-code"


def test_acquire_token_creates_file(tmp_path):
    ws = _init(tmp_path)
    write_token.acquire("session-1", "claude-code", ws)
    assert (loom_dir(ws) / "write_token.json").exists()


def test_acquire_blocked_by_existing(tmp_path):
    ws = _init(tmp_path)
    write_token.acquire("session-1", "claude-code", ws, lease_minutes=60)

    result = write_token.acquire("session-2", "cursor", ws)
    assert result["acquired"] is False
    assert result["holder"] == "claude-code"


def test_same_session_renews(tmp_path):
    ws = _init(tmp_path)
    write_token.acquire("session-1", "claude-code", ws)

    result = write_token.acquire("session-1", "claude-code", ws)
    assert result["acquired"] is True
    assert result.get("renewed") is True


def test_force_acquire(tmp_path):
    ws = _init(tmp_path)
    write_token.acquire("session-1", "claude-code", ws, lease_minutes=60)

    result = write_token.acquire("session-2", "cursor", ws, force=True)
    assert result["acquired"] is True
    assert result.get("forced_from") == "claude-code"


def test_release_token(tmp_path):
    ws = _init(tmp_path)
    write_token.acquire("session-1", "claude-code", ws)

    result = write_token.release("session-1", ws)
    assert result["released"] is True
    assert not (loom_dir(ws) / "write_token.json").exists()


def test_release_wrong_session(tmp_path):
    ws = _init(tmp_path)
    write_token.acquire("session-1", "claude-code", ws)

    result = write_token.release("session-2", ws)
    assert result["released"] is False
    assert result["reason"] == "not_holder"


def test_release_no_token(tmp_path):
    ws = _init(tmp_path)
    result = write_token.release("session-1", ws)
    assert result["released"] is False


def test_status_free(tmp_path):
    ws = _init(tmp_path)
    result = write_token.status(ws)
    assert result["held"] is False


def test_status_held(tmp_path):
    ws = _init(tmp_path)
    write_token.acquire("session-1", "claude-code", ws, lease_minutes=60)

    result = write_token.status(ws)
    assert result["held"] is True
    assert result["actor"] == "claude-code"
    assert result["remaining_seconds"] > 0


def test_expired_token_reclaimable(tmp_path):
    ws = _init(tmp_path)
    # Manually create an expired token
    token_path = loom_dir(ws) / "write_token.json"
    expired = {
        "session_id": "old-session",
        "actor": "windsurf",
        "acquired_at": "2020-01-01T00:00:00+00:00",
        "expires_at": "2020-01-01T00:01:00+00:00",
        "lease_minutes": 1,
    }
    token_path.write_text(json.dumps(expired))

    # New actor should be able to acquire
    result = write_token.acquire("session-2", "cursor", ws)
    assert result["acquired"] is True
    assert result["actor"] == "cursor"


def test_status_expired(tmp_path):
    ws = _init(tmp_path)
    token_path = loom_dir(ws) / "write_token.json"
    expired = {
        "session_id": "old",
        "actor": "windsurf",
        "acquired_at": "2020-01-01T00:00:00+00:00",
        "expires_at": "2020-01-01T00:01:00+00:00",
        "lease_minutes": 1,
    }
    token_path.write_text(json.dumps(expired))

    result = write_token.status(ws)
    assert result["held"] is False
    assert result["expired"] is True
