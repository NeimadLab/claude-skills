"""Cross-model handoff end-to-end test.

This is THE proof that Loom works: model A writes context,
model B reads it back with full fidelity.

Scenario:
  1. "Claude Code" opens a session, makes decisions, logs risks
  2. "Claude Code" closes the session with a summary
  3. "Cursor" opens a new session, reads the handoff summary
  4. Verify: Cursor sees ALL of Claude Code's decisions and risks
  5. "Cursor" makes additional decisions
  6. A third model reads the combined context
"""

import json
import subprocess
from pathlib import Path

import pytest


def loom(*args: str, cwd: Path) -> subprocess.CompletedProcess:
    """Run loom as a subprocess."""
    return subprocess.run(
        ["loom", *args],
        cwd=str(cwd),
        capture_output=True,
        text=True,
        timeout=15,
        check=True,
    )


class TestCrossModelHandoff:
    """End-to-end cross-model handoff test."""

    @pytest.fixture(autouse=True)
    def workspace(self, tmp_path):
        (tmp_path / "pyproject.toml").write_text("[project]\nname='handoff-test'\n")
        (tmp_path / "requirements.txt").write_text("fastapi\nuvicorn\n")
        loom("init", "--non-interactive", cwd=tmp_path)
        self.ws = tmp_path

    def test_full_handoff_scenario(self):
        """The complete cross-model handoff proof."""
        ws = self.ws

        # ── Act 1: Claude Code works ──────────────────────
        loom("session", "open", "claude-code", "--model", "claude-opus-4", cwd=ws)

        # Log decisions
        loom(
            "log",
            "Use FastAPI for the backend",
            "--rationale",
            "Async-native, OpenAPI docs",
            cwd=ws,
        )
        loom("log", "Use PostgreSQL for database", "--rationale", "ACID, JSON support", cwd=ws)
        loom("log", "JWT with RS256 for auth", "--rationale", "Stateless, scalable", cwd=ws)

        # Promote one to validated
        r = loom("search", "FastAPI", "--json", cwd=ws)
        fastapi_id = json.loads(r.stdout)[0]["id"]
        loom("promote", fastapi_id, cwd=ws)

        # Log a goal and a risk
        from loom.memory import MemoryStore
        from loom.models import MemoryEntry, MemoryType

        store = MemoryStore(ws)
        store.write(
            MemoryEntry(
                content="Complete auth migration by Friday",
                type=MemoryType.GOAL,
                actor="claude-code",
            )
        )
        store.write(
            MemoryEntry(
                content="Token revocation not yet implemented",
                type=MemoryType.RISK,
                actor="claude-code",
            )
        )
        store.close()

        # Close session
        loom(
            "session",
            "close",
            "-s",
            "Set up backend architecture: FastAPI + PostgreSQL + JWT",
            cwd=ws,
        )

        # ── Act 2: Cursor picks up ───────────────────────
        loom("session", "open", "cursor", "--model", "gpt-4o", cwd=ws)

        # Read handoff — this is what a real model would do
        r = loom("search", "", "--json", "-t", "decision", cwd=ws)
        decisions = json.loads(r.stdout)

        # VERIFY: Cursor sees all 3 of Claude Code's decisions
        decision_texts = [d["content"] for d in decisions]
        assert any("FastAPI" in d for d in decision_texts), "Cursor should see FastAPI decision"
        assert any("PostgreSQL" in d for d in decision_texts), (
            "Cursor should see PostgreSQL decision"
        )
        assert any("JWT" in d for d in decision_texts), "Cursor should see JWT decision"

        # VERIFY: Cursor sees the validated status
        fastapi_entry = [d for d in decisions if "FastAPI" in d["content"]][0]
        assert fastapi_entry["status"] == "validated"

        # VERIFY: Handoff summary includes goals and risks
        r = loom("search", "", "--json", "-t", "goal", cwd=ws)
        goals = json.loads(r.stdout)
        assert any("auth migration" in g["content"] for g in goals)

        r = loom("search", "", "--json", "-t", "risk", cwd=ws)
        risks = json.loads(r.stdout)
        assert any("Token revocation" in r_["content"] for r_ in risks)

        # VERIFY: Session history shows both actors
        r = loom("session", "list", "--json", cwd=ws)
        sessions = json.loads(r.stdout)
        actors = [s["actor"] for s in sessions]
        assert "claude-code" in actors
        assert "cursor" in actors

        # Cursor adds its own decision
        loom(
            "log",
            "Use Alembic for DB migrations",
            "--rationale",
            "Standard with SQLAlchemy",
            cwd=ws,
        )
        loom("session", "close", "-s", "Started implementing auth endpoints", cwd=ws)

        # ── Act 3: Third model reads everything ──────────
        loom("session", "open", "windsurf", "--model", "claude-sonnet-4", cwd=ws)

        # Context should include everything from both models
        r = loom("context", "--json", cwd=ws)
        ctx = json.loads(r.stdout)

        assert ctx["memory_entries"] >= 5  # 3 decisions + 1 goal + 1 risk + Cursor's decision

        # All decisions from both models visible
        r = loom("search", "", "--json", "-t", "decision", cwd=ws)
        all_decisions = json.loads(r.stdout)
        all_texts = [d["content"] for d in all_decisions]
        assert any("FastAPI" in t for t in all_texts), "Windsurf sees Claude Code's decision"
        assert any("Alembic" in t for t in all_texts), "Windsurf sees Cursor's decision"

        loom("session", "close", cwd=ws)

    def test_handoff_summary_completeness(self):
        """Handoff summary must contain goals, decisions, and risks."""
        ws = self.ws

        # Populate with mixed types
        store = make_store(ws)
        store.write(make_entry("Complete auth", "goal", "claude-code"))
        store.write(make_entry("Use JWT", "decision", "claude-code"))
        store.write(make_entry("No rate limiting", "risk", "claude-code"))
        store.write(make_entry("Redis for caching", "decision", "cursor"))
        store.close()

        # Get handoff
        r = loom("search", "", "--json", "-t", "decision", cwd=ws)
        decisions = json.loads(r.stdout)
        assert len(decisions) >= 2

        r = loom("search", "", "--json", "-t", "goal", cwd=ws)
        goals = json.loads(r.stdout)
        assert len(goals) >= 1

        r = loom("search", "", "--json", "-t", "risk", cwd=ws)
        risks = json.loads(r.stdout)
        assert len(risks) >= 1

    def test_actor_attribution(self):
        """Memory entries must be attributed to the correct actor."""
        ws = self.ws

        store = make_store(ws)
        store.write(make_entry("FastAPI choice", "decision", "claude-code"))
        store.write(make_entry("Alembic choice", "decision", "cursor"))
        store.close()

        r = loom("search", "FastAPI", "--json", cwd=ws)
        entries = json.loads(r.stdout)
        assert entries[0]["actor"] == "claude-code"

        r = loom("search", "Alembic", "--json", cwd=ws)
        entries = json.loads(r.stdout)
        assert entries[0]["actor"] == "cursor"


# ── Helpers ───────────────────────────────────────────────────


def make_store(ws: Path):
    """Create a MemoryStore for a workspace."""
    from loom.memory import MemoryStore

    return MemoryStore(ws)


def make_entry(content: str, type_str: str, actor: str):
    """Create a MemoryEntry with minimal args."""
    from loom.models import MemoryEntry, MemoryType

    return MemoryEntry(
        content=content,
        type=MemoryType(type_str),
        actor=actor,
    )
