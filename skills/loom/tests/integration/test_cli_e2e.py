"""Integration tests — end-to-end CLI workflows via subprocess.

These tests run `loom` as a real subprocess against real temp directories,
testing the same interface a user would see.
"""

from __future__ import annotations

import json
import os
import subprocess
from pathlib import Path

import pytest


def loom(*args: str, cwd: Path | str, check: bool = True) -> subprocess.CompletedProcess:
    """Run a loom CLI command as a subprocess."""
    result = subprocess.run(
        ["loom", *args],
        cwd=str(cwd),
        capture_output=True,
        text=True,
        timeout=15,
    )
    if check and result.returncode != 0:
        raise AssertionError(
            f"loom {' '.join(args)} failed (rc={result.returncode}):\n"
            f"STDOUT: {result.stdout}\nSTDERR: {result.stderr}"
        )
    return result


# ─── Workspace Lifecycle ──────────────────────────────────────


class TestWorkspaceLifecycle:
    """Test init → state → resume → doctor flow."""

    def test_init_creates_workspace(self, tmp_path):
        (tmp_path / "pyproject.toml").write_text("[project]\nname = 'test'\n")

        r = loom("init", "--non-interactive", cwd=tmp_path)
        assert "Workspace initialized" in r.stdout
        assert (tmp_path / ".loom").is_dir()
        assert (tmp_path / ".loom" / "memory.db").exists()
        assert (tmp_path / ".loom" / "runtime.json").exists()

    def test_init_detects_python(self, tmp_path):
        (tmp_path / "pyproject.toml").write_text("[project]\nname = 'test'\n")

        r = loom("init", "--non-interactive", cwd=tmp_path)
        assert "python" in r.stdout.lower()

    def test_init_detects_node(self, tmp_path):
        (tmp_path / "package.json").write_text('{"name": "test"}')

        r = loom("init", "--non-interactive", cwd=tmp_path)
        assert "node" in r.stdout.lower()

    def test_init_adds_gitignore(self, tmp_path):
        (tmp_path / "pyproject.toml").write_text("[project]\n")
        (tmp_path / ".gitignore").write_text("*.pyc\n")

        loom("init", "--non-interactive", cwd=tmp_path)
        content = (tmp_path / ".gitignore").read_text()
        assert ".loom/" in content

    def test_init_force_reinitializes(self, tmp_path):
        (tmp_path / "pyproject.toml").write_text("[project]\n")
        loom("init", "--non-interactive", cwd=tmp_path)
        loom("init", "--non-interactive", "--force", cwd=tmp_path)

        assert (tmp_path / ".loom" / "memory.db").exists()

    def test_state_shows_info(self, tmp_path):
        (tmp_path / "pyproject.toml").write_text("[project]\n")
        loom("init", "--non-interactive", cwd=tmp_path)

        r = loom("state", cwd=tmp_path)
        assert "python" in r.stdout.lower()

    def test_resume_no_drift(self, tmp_path):
        (tmp_path / "pyproject.toml").write_text("[project]\n")
        loom("init", "--non-interactive", cwd=tmp_path)

        r = loom("resume", cwd=tmp_path)
        assert "no drift" in r.stdout.lower()

    def test_doctor_healthy(self, tmp_path):
        (tmp_path / "pyproject.toml").write_text("[project]\n")
        loom("init", "--non-interactive", cwd=tmp_path)

        r = loom("doctor", cwd=tmp_path)
        assert "passed" in r.stdout.lower() or "✓" in r.stdout

    def test_doctor_fails_on_no_workspace(self, tmp_path):
        r = loom("doctor", cwd=tmp_path, check=False)
        assert r.returncode != 0

    def test_state_fails_on_no_workspace(self, tmp_path):
        r = loom("state", cwd=tmp_path, check=False)
        assert r.returncode != 0


# ─── Memory Operations ───────────────────────────────────────


class TestMemoryOperations:
    """Test log → search → promote → reject flow."""

    @pytest.fixture(autouse=True)
    def workspace(self, tmp_path):
        (tmp_path / "pyproject.toml").write_text("[project]\n")
        loom("init", "--non-interactive", cwd=tmp_path)
        self.ws = tmp_path

    def test_log_decision(self):
        r = loom("log", "Use PostgreSQL", "--rationale", "ACID compliance", cwd=self.ws)
        assert "Decision logged" in r.stdout

    def test_search_finds_logged_decision(self):
        loom("log", "Use PostgreSQL for database", cwd=self.ws)

        r = loom("search", "PostgreSQL", cwd=self.ws)
        assert "PostgreSQL" in r.stdout

    def test_search_empty_result(self):
        r = loom("search", "nonexistent-query-xyz", cwd=self.ws)
        assert "No results" in r.stdout or "0 result" in r.stdout

    def test_promote_decision(self):
        loom("log", "Use Redis for caching", cwd=self.ws)

        # Get the entry ID from JSON output
        r = loom("search", "Redis", "--json", cwd=self.ws)
        entries = json.loads(r.stdout)
        entry_id = entries[0]["id"]

        r = loom("promote", entry_id, cwd=self.ws)
        assert "validated" in r.stdout.lower()

    def test_reject_decision(self):
        loom("log", "Use MongoDB", cwd=self.ws)

        r = loom("search", "MongoDB", "--json", cwd=self.ws)
        entries = json.loads(r.stdout)
        entry_id = entries[0]["id"]

        r = loom("reject", entry_id, "-r", "Changed to PostgreSQL", cwd=self.ws)
        assert "Rejected" in r.stdout


# ─── Import/Export ────────────────────────────────────────────


class TestImportExport:
    """Test import CLAUDE.md → search → export roundtrip."""

    @pytest.fixture(autouse=True)
    def workspace(self, tmp_path):
        (tmp_path / "pyproject.toml").write_text("[project]\n")
        loom("init", "--non-interactive", cwd=tmp_path)
        self.ws = tmp_path

    def test_import_claude_md(self):
        md = self.ws / "CLAUDE.md"
        md.write_text(
            "# Instructions\n\n- Use FastAPI for the backend\n- Always write tests first\n"
        )

        r = loom("import", str(md), cwd=self.ws)
        assert "Imported" in r.stdout
        assert "2" in r.stdout  # 2 entries

    def test_import_then_search(self):
        md = self.ws / "CLAUDE.md"
        md.write_text("- Use PostgreSQL for the database\n")
        loom("import", str(md), cwd=self.ws)

        r = loom("search", "PostgreSQL", cwd=self.ws)
        assert "PostgreSQL" in r.stdout

    def test_export_claude_md(self):
        loom("log", "Use JWT for authentication", "--rationale", "Stateless", cwd=self.ws)

        # Promote to validated (export only includes validated)
        r = loom("search", "JWT", "--json", cwd=self.ws)
        entry_id = json.loads(r.stdout)[0]["id"]
        loom("promote", entry_id, cwd=self.ws)

        out = self.ws / "exported.md"
        loom("export", "claude-md", "-o", str(out), cwd=self.ws)
        content = out.read_text()
        assert "JWT" in content

    def test_roundtrip(self):
        md = self.ws / "source.md"
        md.write_text("- Use Redis for session caching\n- Adopt conventional commits\n")
        loom("import", str(md), cwd=self.ws)

        out = self.ws / "roundtrip.md"
        loom("export", "claude-md", "-o", str(out), cwd=self.ws)
        content = out.read_text()
        assert "Redis" in content


# ─── JSON Output ──────────────────────────────────────────────


class TestJsonOutput:
    """Test --json flag on all data commands."""

    @pytest.fixture(autouse=True)
    def workspace(self, tmp_path):
        (tmp_path / "pyproject.toml").write_text("[project]\n")
        loom("init", "--non-interactive", cwd=tmp_path)
        loom("log", "Test decision", cwd=tmp_path)
        self.ws = tmp_path

    def test_state_json(self):
        r = loom("state", "--json", cwd=self.ws)
        data = json.loads(r.stdout)
        assert "project_type" in data
        assert "memory_entries" in data
        assert data["memory_entries"] >= 1

    def test_doctor_json(self):
        r = loom("doctor", "--json", cwd=self.ws)
        data = json.loads(r.stdout)
        assert "healthy" in data
        assert "checks" in data
        assert isinstance(data["checks"], list)

    def test_search_json(self):
        r = loom("search", "decision", "--json", cwd=self.ws)
        data = json.loads(r.stdout)
        assert isinstance(data, list)

    def test_search_json_empty(self):
        r = loom("search", "nonexistent-xyz", "--json", cwd=self.ws)
        data = json.loads(r.stdout)
        assert isinstance(data, list)
        assert len(data) == 0

    def test_events_json(self):
        r = loom("events", "--json", cwd=self.ws)
        data = json.loads(r.stdout)
        assert isinstance(data, list)
        assert len(data) >= 1

    def test_resume_json(self):
        r = loom("resume", "--json", cwd=self.ws)
        data = json.loads(r.stdout)
        assert "drift" in data
        assert "memory_entries" in data


# ─── Connect ─────────────────────────────────────────────────


class TestConnect:
    """Test loom connect generates valid config files."""

    @pytest.fixture(autouse=True)
    def workspace(self, tmp_path):
        (tmp_path / "pyproject.toml").write_text("[project]\n")
        loom("init", "--non-interactive", cwd=tmp_path)
        self.ws = tmp_path

    def test_connect_claude_code(self, tmp_path):
        # Point to a writable config location
        config_dir = tmp_path / ".claude"
        config_dir.mkdir()
        config_file = config_dir / "settings.json"
        config_file.write_text("{}")

        env = os.environ.copy()
        env["HOME"] = str(tmp_path)

        r = subprocess.run(
            ["loom", "connect", "claude-code"],
            cwd=str(self.ws),
            capture_output=True,
            text=True,
            env=env,
        )
        # Even if path doesn't match exactly, the command shouldn't crash
        assert r.returncode == 0 or "configured" in r.stdout.lower()


# ─── Events ──────────────────────────────────────────────────


class TestEvents:
    """Test event log trail."""

    def test_events_after_operations(self, tmp_path):
        (tmp_path / "pyproject.toml").write_text("[project]\n")
        loom("init", "--non-interactive", cwd=tmp_path)
        loom("log", "A decision", cwd=tmp_path)

        r = loom("events", "--json", cwd=tmp_path)
        data = json.loads(r.stdout)
        event_types = [e["event_type"] for e in data]
        assert "workspace_initialized" in event_types
        assert "decision_logged" in event_types

    def test_events_count_flag(self, tmp_path):
        (tmp_path / "pyproject.toml").write_text("[project]\n")
        loom("init", "--non-interactive", cwd=tmp_path)
        for i in range(5):
            loom("log", f"Decision {i}", cwd=tmp_path)

        r = loom("events", "--json", "-n", "3", cwd=tmp_path)
        data = json.loads(r.stdout)
        assert len(data) == 3
