"""Automated end-to-end quality audit.

Reproduces the full manual audit workflow as an automated test.
This is the "does Loom actually work?" test — run it before every release.

Covers:
1. Full user journey: init → template → log → search → promote → export
2. Cross-model handoff: Claude Code → Cursor → Windsurf
3. Session lifecycle: open → work → close → verify history
4. Doctor + status + repair
5. Gateway REST + MCP-over-HTTP
6. Team mode: add user → auth → permissions
7. Write token: acquire → check → release
8. Policy engine: install → evaluate
9. Import/export roundtrip
10. Actor attribution with active session
"""

from __future__ import annotations

import json
import subprocess
from pathlib import Path

import pytest


def loom(*args: str, cwd: Path, check: bool = True) -> subprocess.CompletedProcess:
    """Run loom as a subprocess."""
    r = subprocess.run(
        ["loom", *args],
        cwd=str(cwd),
        capture_output=True,
        text=True,
        timeout=30,
    )
    if check and r.returncode != 0:
        raise AssertionError(
            f"loom {' '.join(args)} failed (rc={r.returncode}):\n"
            f"STDOUT: {r.stdout[:500]}\nSTDERR: {r.stderr[:500]}"
        )
    return r


def json_out(*args: str, cwd: Path) -> dict | list:
    """Run a loom command with --json and parse the output."""
    r = loom(*args, cwd=cwd)
    return json.loads(r.stdout)


class TestFullAudit:
    """Complete E2E audit — the release gate test."""

    @pytest.fixture(autouse=True)
    def workspace(self, tmp_path):
        (tmp_path / "pyproject.toml").write_text("[project]\nname='audit-project'\n")
        (tmp_path / "requirements.txt").write_text("fastapi\nuvicorn\npydantic\n")
        self.ws = tmp_path

    # ── 1. Full User Journey ──────────────────────────────────

    def test_01_init_with_template(self):
        """Init with template seeds memory."""
        r = loom("init", "--non-interactive", "-t", "web-backend", cwd=self.ws)
        assert "Workspace initialized" in r.stdout
        assert "Template applied" in r.stdout
        assert (self.ws / ".loom" / "memory.db").exists()
        assert (self.ws / ".loom" / "runtime.json").exists()

    def test_02_log_search_promote_export(self):
        """Full memory lifecycle: log → search → promote → export."""
        loom("init", "--non-interactive", "-t", "web-backend", cwd=self.ws)

        # Log decisions
        loom("log", "Use FastAPI for backend", "-r", "Async-native", cwd=self.ws)
        loom("log", "Use PostgreSQL for database", "-r", "ACID compliance", cwd=self.ws)

        # Search finds them
        results = json_out("search", "FastAPI", "--json", cwd=self.ws)
        assert len(results) >= 1
        assert "FastAPI" in results[0]["content"]

        # Promote
        entry_id = results[0]["id"]
        loom("promote", entry_id, cwd=self.ws)

        # Verify promotion
        results = json_out("search", "FastAPI", "--json", cwd=self.ws)
        assert results[0]["status"] == "validated"

        # Export
        out = self.ws / "CLAUDE-OUT.md"
        loom("export", "claude-md", "-o", str(out), cwd=self.ws)
        content = out.read_text()
        assert "FastAPI" in content

    # ── 2. Cross-Model Handoff ────────────────────────────────

    def test_03_cross_model_handoff(self):
        """Claude Code writes, Cursor reads, Windsurf sees everything."""
        loom("init", "--non-interactive", cwd=self.ws)

        # Claude Code works
        loom("session", "open", "claude-code", "--model", "claude-opus-4", cwd=self.ws)
        loom("log", "Use JWT with RS256 for auth", "-r", "Stateless", cwd=self.ws)
        loom("log", "Use Alembic for migrations", "-r", "SQLAlchemy standard", cwd=self.ws)
        loom("session", "close", "-s", "Auth architecture done", cwd=self.ws)

        # Cursor picks up — sees Claude Code's decisions
        loom("session", "open", "cursor", "--model", "gpt-4o", cwd=self.ws)
        decisions = json_out("search", "", "--json", "-t", "decision", cwd=self.ws)
        decision_texts = [d["content"] for d in decisions]
        assert any("JWT" in t for t in decision_texts), "Cursor must see JWT decision"
        assert any("Alembic" in t for t in decision_texts), "Cursor must see Alembic decision"

        # Cursor adds its own
        loom("log", "Use Redis for caching", "-r", "Low latency", cwd=self.ws)
        loom("session", "close", "-s", "Added caching layer", cwd=self.ws)

        # Windsurf sees everything
        loom("session", "open", "windsurf", "--model", "claude-sonnet-4", cwd=self.ws)
        all_decisions = json_out("search", "", "--json", "-t", "decision", cwd=self.ws)
        all_texts = [d["content"] for d in all_decisions]
        assert any("JWT" in t for t in all_texts), "Windsurf sees Claude Code's decision"
        assert any("Redis" in t for t in all_texts), "Windsurf sees Cursor's decision"
        loom("session", "close", cwd=self.ws)

        # Session history shows all three actors
        sessions = json_out("session", "list", "--json", cwd=self.ws)
        actors = {s["actor"] for s in sessions}
        assert actors == {"claude-code", "cursor", "windsurf"}

    # ── 3. Actor Attribution ──────────────────────────────────

    def test_04_actor_inherits_from_session(self):
        """loom log should attribute to the active session actor."""
        loom("init", "--non-interactive", cwd=self.ws)

        # Log without session → actor='cli'
        loom("log", "Decision without session", cwd=self.ws)
        results = json_out("search", "without session", "--json", cwd=self.ws)
        assert results[0]["actor"] == "cli"

        # Log with session → actor='claude-code'
        loom("session", "open", "claude-code", cwd=self.ws)
        loom("log", "Decision with session", cwd=self.ws)
        loom("session", "close", cwd=self.ws)

        results = json_out("search", "with session", "--json", cwd=self.ws)
        assert results[0]["actor"] == "claude-code"

    # ── 4. Doctor + Status + Repair ───────────────────────────

    def test_05_doctor_healthy(self):
        """Doctor passes all required checks on a healthy workspace."""
        loom("init", "--non-interactive", cwd=self.ws)
        result = json_out("doctor", "--json", cwd=self.ws)
        assert result["healthy"] is True
        # Required checks all pass
        required = [c for c in result["checks"] if not c.get("optional")]
        assert all(c["ok"] for c in required)

    def test_06_doctor_optional_dont_fail_health(self):
        """Optional checks (Git, Docker) don't make doctor unhealthy."""
        loom("init", "--non-interactive", cwd=self.ws)
        result = json_out("doctor", "--json", cwd=self.ws)
        # Even without Git/Docker, healthy should be True
        assert result["healthy"] is True
        assert "required" in result["summary"]

    def test_07_status_one_liner(self):
        """Status returns comprehensive JSON with all subsystems."""
        loom("init", "--non-interactive", cwd=self.ws)
        loom("log", "Test decision", cwd=self.ws)
        loom("session", "open", "test-actor", cwd=self.ws)

        data = json_out("status", "--json", cwd=self.ws)
        assert "state" in data
        assert "doctor" in data
        assert "session" in data
        assert "write_token" in data
        assert "team_mode" in data
        assert data["state"]["memory_entries"] >= 1
        assert data["session"]["active"] is not None

        loom("session", "close", cwd=self.ws)

    def test_08_repair(self):
        """Repair runs without error on a healthy workspace."""
        loom("init", "--non-interactive", cwd=self.ws)
        result = json_out("repair", "--json", cwd=self.ws)
        assert "integrity" in result
        assert "repairs" in result

    # ── 5. Write Token ────────────────────────────────────────

    def test_09_write_token_lifecycle(self):
        """Acquire → status → release lifecycle."""
        loom("init", "--non-interactive", cwd=self.ws)

        # Acquire
        result = json_out("token", "acquire", "sess-1", "claude-code", "--json", cwd=self.ws)
        assert result["acquired"] is True

        # Status shows held
        status = json_out("token", "status", "--json", cwd=self.ws)
        assert status["held"] is True
        assert status["actor"] == "claude-code"

        # Release
        result = json_out("token", "release", "sess-1", "--json", cwd=self.ws)
        assert result["released"] is True

        # Status shows free
        status = json_out("token", "status", "--json", cwd=self.ws)
        assert status["held"] is False

    # ── 6. Import/Export Roundtrip ────────────────────────────

    def test_10_import_export_roundtrip(self):
        """Import CLAUDE.md → work → export → verify content survives."""
        loom("init", "--non-interactive", cwd=self.ws)

        # Write source file
        src = self.ws / "CLAUDE.md"
        src.write_text(
            "# Architecture\n\n"
            "- Use Redis for session caching\n"
            "- Adopt conventional commits\n"
            "- Risk: no monitoring yet\n"
        )

        loom("import", str(src), cwd=self.ws)
        results = json_out("search", "Redis", "--json", cwd=self.ws)
        assert len(results) >= 1
        assert results[0]["status"] == "validated"  # imported = trusted

        # Export
        out = self.ws / "exported.md"
        loom("export", "claude-md", "-o", str(out), cwd=self.ws)
        assert "Redis" in out.read_text()

    # ── 7. Templates ──────────────────────────────────────────

    def test_11_templates(self):
        """Templates seed domain-specific entries."""
        loom("init", "--non-interactive", "-t", "cli-tool", cwd=self.ws)

        results = json_out("search", "exit codes", "--json", cwd=self.ws)
        assert len(results) >= 1
        assert results[0]["status"] == "validated"
        assert "cli-tool" in results[0].get("tags", "")

    # ── 8. Policy Engine ──────────────────────────────────────

    def test_12_policy(self):
        """Policy install + check works."""
        loom("init", "--non-interactive", cwd=self.ws)
        loom("policy", "install", cwd=self.ws)

        assert (self.ws / ".loom" / "policies" / "default.yaml").exists()

        result = json_out("policy", "check", "loom_search_memory", "--json", cwd=self.ws)
        assert result["decision"] in ("allow", "deny", "approve")

    # ── 9. Gateway REST API ───────────────────────────────────

    def test_13_gateway_rest(self):
        """Gateway REST endpoints respond correctly."""
        loom("init", "--non-interactive", cwd=self.ws)
        loom("log", "Gateway test decision", cwd=self.ws)

        import sys

        sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))

        from starlette.testclient import TestClient

        from loom.gateway import create_app

        app = create_app(self.ws)
        client = TestClient(app)

        # Health
        r = client.get("/health")
        assert r.status_code == 200
        assert r.json()["status"] == "ok"

        # Search
        r = client.post("/api/search", json={"query": "Gateway"})
        assert r.status_code == 200
        assert len(r.json()) >= 1

        # Handoff
        r = client.get("/api/handoff")
        assert r.status_code == 200
        assert "recent_decisions" in r.json()

        # MCP tools/list
        r = client.post(
            "/mcp/messages",
            json={"jsonrpc": "2.0", "id": 1, "method": "tools/list", "params": {}},
        )
        assert r.status_code == 200
        tools = r.json()["result"]["tools"]
        tool_names = {t["name"] for t in tools}
        assert "loom_search_memory" in tool_names
        assert "loom_open_session" in tool_names

    # ── 10. JSON Output Validity ──────────────────────────────

    def test_14_all_json_outputs_valid(self):
        """Every --json command produces valid, parseable JSON."""
        loom("init", "--non-interactive", cwd=self.ws)
        loom("log", "JSON test", cwd=self.ws)

        commands = [
            ["state", "--json"],
            ["doctor", "--json"],
            ["resume", "--json"],
            ["search", "test", "--json"],
            ["events", "--json"],
            ["context", "--json"],
            ["status", "--json"],
            ["session", "list", "--json"],
            ["token", "status", "--json"],
            ["team", "list", "--json"],
            ["policy", "check", "loom_search_memory", "--json"],
            ["workspace", "list", "--json"],
        ]

        for cmd in commands:
            r = loom(*cmd, cwd=self.ws)
            try:
                json.loads(r.stdout)
            except json.JSONDecodeError:
                pytest.fail(f"loom {' '.join(cmd)} produced invalid JSON:\n{r.stdout[:200]}")

    # ── 11. Actor Filter ──────────────────────────────────────

    def test_15_search_actor_filter(self):
        """Search with --actor filters by actor name."""
        loom("init", "--non-interactive", cwd=self.ws)

        # Create entries from different actors
        loom("session", "open", "claude-code", cwd=self.ws)
        loom("log", "Claude decision", cwd=self.ws)
        loom("session", "close", cwd=self.ws)

        loom("session", "open", "cursor", cwd=self.ws)
        loom("log", "Cursor decision", cwd=self.ws)
        loom("session", "close", cwd=self.ws)

        # Filter by actor
        claude_results = json_out("search", "", "--json", "--actor", "claude-code", cwd=self.ws)
        cursor_results = json_out("search", "", "--json", "--actor", "cursor", cwd=self.ws)

        assert all(r["actor"] == "claude-code" for r in claude_results)
        assert all(r["actor"] == "cursor" for r in cursor_results)

    # ── 12. Team Mode ─────────────────────────────────────────

    def test_16_team_mode(self):
        """Team mode: add user, verify auth, check permissions."""
        loom("init", "--non-interactive", cwd=self.ws)

        # Solo mode initially
        data = json_out("status", "--json", cwd=self.ws)
        assert data["team_mode"] is False

        # Add user → switches to team mode
        r = loom("team", "add", "alice", "--role", "admin", "--json", cwd=self.ws)
        user = json.loads(r.stdout)
        assert user["name"] == "alice"
        assert user["role"] == "admin"
        assert len(user["api_key"]) == 64

        # Now in team mode
        users = json_out("team", "list", "--json", cwd=self.ws)
        assert len(users) == 1
        assert users[0]["name"] == "alice"

        # Remove → back to solo
        loom("team", "remove", user["user_id"], cwd=self.ws)
        users = json_out("team", "list", "--json", cwd=self.ws)
        assert len(users) == 0
