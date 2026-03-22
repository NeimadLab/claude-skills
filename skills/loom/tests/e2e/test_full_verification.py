"""End-to-end verification: exercises every CLI command and validates output.

Run with: pytest tests/e2e/test_full_verification.py -v
Or standalone: python tests/e2e/test_full_verification.py

This is the "does it actually work?" test suite. Every command is tested
with real subprocess calls against real temp directories. JSON output is
parsed and validated. This catches:
- Broken imports
- Missing CLI wiring
- JSON serialization errors
- Filesystem permission issues
- Version mismatches
"""

from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path

import pytest

TIMEOUT = 30


def loom(
    *args: str,
    cwd: Path,
    check: bool = True,
    env: dict | None = None,
) -> subprocess.CompletedProcess:
    """Run loom as a real subprocess."""
    run_env = os.environ.copy()
    if env:
        run_env.update(env)
    result = subprocess.run(
        ["loom", *args],
        cwd=str(cwd),
        capture_output=True,
        text=True,
        timeout=TIMEOUT,
        env=run_env,
    )
    if check and result.returncode != 0:
        raise AssertionError(
            f"loom {' '.join(args)} failed (rc={result.returncode}):\n"
            f"STDOUT: {result.stdout[:500]}\nSTDERR: {result.stderr[:500]}"
        )
    return result


@pytest.fixture
def workspace(tmp_path):
    """Create and initialize a workspace with content."""
    (tmp_path / "pyproject.toml").write_text("[project]\nname='e2e-test'\n")
    (tmp_path / "requirements.txt").write_text("fastapi\nuvicorn\n")
    loom("init", "--non-interactive", "-t", "web-backend", cwd=tmp_path)
    return tmp_path


# ═══════════════════════════════════════════════════════════════
# SECTION 1: Workspace lifecycle
# ═══════════════════════════════════════════════════════════════


class TestWorkspaceLifecycle:
    def test_init_creates_loom_dir(self, tmp_path):
        (tmp_path / "pyproject.toml").write_text("[project]\n")
        loom("init", "--non-interactive", cwd=tmp_path)
        assert (tmp_path / ".loom").is_dir()
        assert (tmp_path / ".loom" / "memory.db").exists()
        assert (tmp_path / ".loom" / "runtime.json").exists()
        assert (tmp_path / ".loom" / "events.jsonl").exists()

    def test_init_with_template_seeds_memory(self, tmp_path):
        (tmp_path / "pyproject.toml").write_text("[project]\n")
        loom("init", "--non-interactive", "-t", "cli-tool", cwd=tmp_path)
        r = loom("search", "", "--json", cwd=tmp_path)
        entries = json.loads(r.stdout)
        assert len(entries) >= 4

    def test_init_auto_imports_claude_md(self, tmp_path):
        (tmp_path / "pyproject.toml").write_text("[project]\n")
        (tmp_path / "CLAUDE.md").write_text(
            "- Use PostgreSQL for database\n- Always prefer explicit error types\n"
        )
        loom("init", "--non-interactive", cwd=tmp_path)
        r = loom("search", "PostgreSQL", "--json", cwd=tmp_path)
        assert len(json.loads(r.stdout)) >= 1

    def test_state_json_valid(self, workspace):
        r = loom("state", "--json", cwd=workspace)
        d = json.loads(r.stdout)
        assert d["project_type"] == "python"
        assert d["memory_entries"] >= 5  # from template

    def test_resume_json_valid(self, workspace):
        r = loom("resume", "--json", cwd=workspace)
        d = json.loads(r.stdout)
        assert "drift" in d
        assert "memory_entries" in d

    def test_status_json_all_keys(self, workspace):
        r = loom("status", "--json", cwd=workspace)
        d = json.loads(r.stdout)
        assert "state" in d
        assert "doctor" in d
        assert "session" in d
        assert "write_token" in d
        assert "team_mode" in d

    def test_doctor_json_valid(self, workspace):
        r = loom("doctor", "--json", cwd=workspace)
        d = json.loads(r.stdout)
        assert "healthy" in d
        assert "checks" in d
        assert isinstance(d["checks"], list)

    def test_events_json_valid(self, workspace):
        r = loom("events", "--json", cwd=workspace)
        d = json.loads(r.stdout)
        assert isinstance(d, list)
        assert len(d) >= 1
        assert "event_type" in d[0]


# ═══════════════════════════════════════════════════════════════
# SECTION 2: Memory operations
# ═══════════════════════════════════════════════════════════════


class TestMemoryOperations:
    def test_log_search_promote_reject_cycle(self, workspace):
        # Log two decisions
        loom("log", "Use JWT for auth", "-r", "Stateless", cwd=workspace)
        loom("log", "Use MongoDB", "-r", "Wrong choice", cwd=workspace)

        # Search
        r = loom("search", "JWT", "--json", cwd=workspace)
        jwt = json.loads(r.stdout)
        assert len(jwt) >= 1
        assert jwt[0]["status"] == "hypothesis"

        # Promote
        loom("promote", jwt[0]["id"], cwd=workspace)
        r = loom("search", "JWT", "--json", cwd=workspace)
        assert json.loads(r.stdout)[0]["status"] == "validated"

        # Reject
        r = loom("search", "MongoDB", "--json", cwd=workspace)
        mongo_id = json.loads(r.stdout)[0]["id"]
        loom("reject", mongo_id, "-r", "Wrong database choice", cwd=workspace)
        r = loom("search", "MongoDB", "--json", cwd=workspace)
        assert json.loads(r.stdout)[0]["status"] == "rejected"

    def test_context_json_valid(self, workspace):
        loom("log", "Test decision for context", cwd=workspace)
        r = loom("context", "--json", cwd=workspace)
        d = json.loads(r.stdout)
        assert "memory_entries" in d
        assert "project_type" in d


# ═══════════════════════════════════════════════════════════════
# SECTION 3: Sessions and write tokens
# ═══════════════════════════════════════════════════════════════


class TestSessionsAndTokens:
    def test_full_session_lifecycle(self, workspace):
        # Open
        r = loom("session", "open", "claude-code", "--model", "opus", "--json", cwd=workspace)
        session = json.loads(r.stdout)
        assert session["status"] == "active"
        sid = session["id"]

        # List
        r = loom("session", "list", "--json", cwd=workspace)
        sessions = json.loads(r.stdout)
        assert any(s["id"] == sid for s in sessions)

        # Acquire token
        r = loom("token", "acquire", sid, "claude-code", "--json", cwd=workspace)
        tok = json.loads(r.stdout)
        assert tok["acquired"] is True

        # Token status
        r = loom("token", "status", "--json", cwd=workspace)
        assert json.loads(r.stdout)["held"] is True

        # Release
        r = loom("token", "release", sid, "--json", cwd=workspace)
        assert json.loads(r.stdout)["released"] is True

        # Close session
        r = loom("session", "close", "-s", "E2E test done", "--json", cwd=workspace)
        assert json.loads(r.stdout)["status"] == "closed"


# ═══════════════════════════════════════════════════════════════
# SECTION 4: Import / Export
# ═══════════════════════════════════════════════════════════════


class TestImportExport:
    def test_roundtrip(self, workspace):
        # Import
        md = workspace / "SOURCE.md"
        md.write_text("- Use Redis for caching\n- Always validate input\n")
        loom("import", str(md), cwd=workspace)

        # Verify imported
        r = loom("search", "Redis", "--json", cwd=workspace)
        assert len(json.loads(r.stdout)) >= 1

        # Export
        out = workspace / "exported.md"
        loom("export", "claude-md", "-o", str(out), cwd=workspace)
        content = out.read_text()
        assert "Redis" in content


# ═══════════════════════════════════════════════════════════════
# SECTION 5: Policy engine
# ═══════════════════════════════════════════════════════════════


class TestPolicy:
    def test_install_and_check(self, workspace):
        loom("policy", "install", cwd=workspace)
        assert (workspace / ".loom" / "policies" / "default.yaml").exists()

        r = loom("policy", "check", "loom_search_memory", "--json", cwd=workspace)
        d = json.loads(r.stdout)
        assert d["decision"] in ("allow", "deny", "approve")


# ═══════════════════════════════════════════════════════════════
# SECTION 6: Recovery
# ═══════════════════════════════════════════════════════════════


class TestRecovery:
    def test_repair_json(self, workspace):
        r = loom("repair", "--json", cwd=workspace)
        d = json.loads(r.stdout)
        assert "integrity" in d
        assert "repairs" in d

    def test_decay_dry_run(self, workspace):
        r = loom("decay", "--ttl", "30", "--dry-run", "--json", cwd=workspace)
        d = json.loads(r.stdout)
        assert "dry_run" in d


# ═══════════════════════════════════════════════════════════════
# SECTION 7: Team mode
# ═══════════════════════════════════════════════════════════════


class TestTeamMode:
    def test_add_list_remove(self, workspace):
        r = loom("team", "add", "alice", "--role", "admin", "--json", cwd=workspace)
        user = json.loads(r.stdout)
        assert user["name"] == "alice"
        assert user["role"] == "admin"

        r = loom("team", "list", "--json", cwd=workspace)
        users = json.loads(r.stdout)
        assert len(users) == 1

        loom("team", "remove", user["user_id"], cwd=workspace)
        r = loom("team", "list", "--json", cwd=workspace)
        assert len(json.loads(r.stdout)) == 0


# ═══════════════════════════════════════════════════════════════
# SECTION 8: Multi-workspace
# ═══════════════════════════════════════════════════════════════


class TestMultiWorkspace:
    def test_register_list(self, workspace):
        r = loom(
            "workspace", "register", str(workspace), "-n", "test-project", "--json", cwd=workspace
        )
        ws = json.loads(r.stdout)
        assert ws["name"] == "test-project"

        r = loom("workspace", "list", "--json", cwd=workspace)
        workspaces = json.loads(r.stdout)
        assert len(workspaces) >= 1


# ═══════════════════════════════════════════════════════════════
# SECTION 9: Benchmark
# ═══════════════════════════════════════════════════════════════


class TestBenchmark:
    def test_benchmark_json(self, workspace):
        r = loom("benchmark", "--json", cwd=workspace)
        d = json.loads(r.stdout)
        assert "init" in d
        assert "search" in d
        assert d["search"]["p95_ms"] < 10  # performance gate


# ═══════════════════════════════════════════════════════════════
# SECTION 10: Cross-model handoff (the proof)
# ═══════════════════════════════════════════════════════════════


class TestCrossModelHandoff:
    def test_model_a_writes_model_b_reads(self, workspace):
        """THE test: Claude Code writes, Cursor reads, nothing is lost."""
        # Model A works
        loom("session", "open", "claude-code", "--model", "opus", cwd=workspace)
        loom("log", "Use FastAPI for API", "-r", "Async, OpenAPI", cwd=workspace)
        loom("log", "Use PostgreSQL", "-r", "ACID", cwd=workspace)
        loom("session", "close", "-s", "Backend arch done", cwd=workspace)

        # Model B reads
        loom("session", "open", "cursor", "--model", "gpt-4o", cwd=workspace)

        # Verify B sees A's decisions
        r = loom("search", "", "--json", "-t", "decision", cwd=workspace)
        decisions = json.loads(r.stdout)
        contents = [d["content"] for d in decisions]
        assert any("FastAPI" in c for c in contents), "Cursor must see FastAPI decision"
        assert any("PostgreSQL" in c for c in contents), "Cursor must see PostgreSQL decision"

        # Verify session history
        r = loom("session", "list", "--json", cwd=workspace)
        actors = [s["actor"] for s in json.loads(r.stdout)]
        assert "claude-code" in actors
        assert "cursor" in actors

        loom("session", "close", cwd=workspace)


# ═══════════════════════════════════════════════════════════════
# SECTION 11: Templates
# ═══════════════════════════════════════════════════════════════


class TestTemplates:
    def test_list(self, tmp_path):
        r = loom("templates", "list", cwd=tmp_path)
        assert "web-backend" in r.stdout
        assert "cli-tool" in r.stdout

    def test_apply(self, workspace):
        loom("templates", "apply", "data-pipeline", cwd=workspace)
        r = loom("search", "idempotent", "--json", cwd=workspace)
        assert len(json.loads(r.stdout)) >= 1


# ═══════════════════════════════════════════════════════════════
# Standalone runner
# ═══════════════════════════════════════════════════════════════

if __name__ == "__main__":
    sys.exit(pytest.main([__file__, "-v", "--tb=short"]))
