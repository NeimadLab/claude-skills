"""Tests for workspace state and doctor."""

from pathlib import Path

from loom.events import emit
from loom.memory import MemoryStore
from loom.models import Event
from loom.runtime import compute_identity, save_identity
from loom.state import doctor_check, get_workspace_state


def _init_workspace(tmp_path: Path) -> None:
    """Helper: create a minimal initialized workspace."""
    (tmp_path / ".loom").mkdir()
    identity = compute_identity(tmp_path)
    save_identity(identity, tmp_path)
    store = MemoryStore(tmp_path)
    store.close()
    emit(Event(event_type="workspace_initialized"), tmp_path)


def test_get_workspace_state_uninitialized(tmp_path):
    state = get_workspace_state(tmp_path)
    assert state["loom_initialized"] is False


def test_get_workspace_state_initialized(tmp_path):
    (tmp_path / "pyproject.toml").write_text("[project]")
    _init_workspace(tmp_path)
    state = get_workspace_state(tmp_path)
    assert state["loom_initialized"] is True
    assert state["project_type"] == "python"
    assert state["identity_drift"] == "none"
    assert state["event_count"] >= 1


def test_doctor_healthy(tmp_path):
    (tmp_path / "pyproject.toml").write_text("[project]")
    _init_workspace(tmp_path)
    result = doctor_check(tmp_path)
    assert result["healthy"] is True
    assert any(c["name"] == ".loom/ directory" and c["ok"] for c in result["checks"])


def test_doctor_unhealthy(tmp_path):
    result = doctor_check(tmp_path)
    assert result["healthy"] is False
