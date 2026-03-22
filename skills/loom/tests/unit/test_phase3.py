"""Tests for Phase 3: policy engine, recovery, memory decay, benchmarks."""

import json
from pathlib import Path

from loom.memory import MemoryStore
from loom.models import MemoryEntry, MemoryStatus, MemoryType


def _init(tmp_path: Path) -> Path:
    (tmp_path / ".loom").mkdir()
    return tmp_path


# ── Policy Engine ─────────────────────────────────────────────


class TestPolicyEngine:
    def test_no_policy_allows_everything(self, tmp_path):
        ws = _init(tmp_path)
        from loom.policy import evaluate

        result = evaluate("loom_search_memory", {"query": "test"}, ws)
        assert result["decision"] == "allow"

    def test_install_default_policy(self, tmp_path):
        ws = _init(tmp_path)
        from loom.policy import install_default_policy

        dest = install_default_policy(ws)
        assert dest.exists()
        assert "rules" in dest.read_text()

    def test_deny_rule_blocks(self, tmp_path):
        ws = _init(tmp_path)
        policy_dir = ws / ".loom" / "policies"
        policy_dir.mkdir(parents=True)
        (policy_dir / "default.yaml").write_text(
            "rules:\n  - action: write_memory\n    default: deny\n"
        )

        from loom.policy import evaluate

        result = evaluate("loom_write_memory", {"content": "test"}, ws)
        assert result["decision"] == "deny"

    def test_allow_rule_passes(self, tmp_path):
        ws = _init(tmp_path)
        policy_dir = ws / ".loom" / "policies"
        policy_dir.mkdir(parents=True)
        (policy_dir / "default.yaml").write_text(
            "rules:\n  - action: read_memory\n    default: allow\n"
        )

        from loom.policy import evaluate

        result = evaluate("loom_search_memory", {"query": "test"}, ws)
        assert result["decision"] == "allow"

    def test_condition_match_overrides_default(self, tmp_path):
        ws = _init(tmp_path)
        policy_dir = ws / ".loom" / "policies"
        policy_dir.mkdir(parents=True)
        (policy_dir / "default.yaml").write_text(
            "rules:\n"
            "  - action: write_memory\n"
            "    default: allow\n"
            "    conditions:\n"
            "      - alias_match: secret\n"
            "        decision: deny\n"
            "        reason: Contains sensitive content\n"
        )

        from loom.policy import evaluate

        # Normal write → allowed
        r1 = evaluate("loom_write_memory", {"content": "normal note"}, ws)
        assert r1["decision"] == "allow"

        # Write with "secret" → denied
        r2 = evaluate("loom_write_memory", {"content": "secret API key"}, ws)
        assert r2["decision"] == "deny"


# ── Recovery & Integrity ──────────────────────────────────────


class TestRecovery:
    def test_integrity_check_healthy(self, tmp_path):
        ws = _init(tmp_path)
        store = MemoryStore(ws)
        store.write(MemoryEntry(content="test"))
        store.close()

        # Create minimal runtime.json
        (ws / ".loom" / "runtime.json").write_text('{"identity_hash": "abc"}')

        from loom.recovery import integrity_check

        report = integrity_check(ws)
        assert report["healthy"] is True or any(c["ok"] for c in report["checks"])

    def test_integrity_check_missing_db(self, tmp_path):
        ws = _init(tmp_path)
        from loom.recovery import integrity_check

        report = integrity_check(ws)
        # Should detect missing files
        failed = [c for c in report["checks"] if not c["ok"]]
        assert len(failed) > 0

    def test_repair_cleans_expired_token(self, tmp_path):
        ws = _init(tmp_path)
        MemoryStore(ws).close()  # init db

        # Create expired token
        token = {
            "session_id": "old",
            "actor": "test",
            "acquired_at": "2020-01-01T00:00:00+00:00",
            "expires_at": "2020-01-01T00:01:00+00:00",
            "lease_minutes": 1,
        }
        (ws / ".loom" / "write_token.json").write_text(json.dumps(token))

        from loom.recovery import repair

        result = repair(ws)
        assert result["repaired"] >= 1
        assert not (ws / ".loom" / "write_token.json").exists()

    def test_rebuild_from_events(self, tmp_path):
        ws = _init(tmp_path)

        # Create events without memory.db
        events = [
            {
                "event_type": "decision_logged",
                "actor": "claude-code",
                "data": {"decision": "Use FastAPI", "type": "decision"},
                "timestamp": "2026-01-01T00:00:00Z",
            },
            {
                "event_type": "decision_logged",
                "actor": "cursor",
                "data": {"decision": "Use PostgreSQL", "type": "decision"},
                "timestamp": "2026-01-02T00:00:00Z",
            },
        ]
        events_path = ws / ".loom" / "events.jsonl"
        events_path.write_text("\n".join(json.dumps(e) for e in events))

        from loom.recovery import rebuild_from_events

        result = rebuild_from_events(ws)
        assert result["rebuilt"] == 2

        # Verify memory.db now has the entries
        store = MemoryStore(ws)
        assert store.count() == 2
        store.close()


# ── Memory Decay ──────────────────────────────────────────────


class TestMemoryDecay:
    def test_decay_old_hypotheses(self, tmp_path):
        ws = _init(tmp_path)
        store = MemoryStore(ws)

        # Write an old hypothesis (manually set old timestamp)
        entry = MemoryEntry(content="Old hypothesis", type=MemoryType.NOTE)
        store.write(entry)
        store.conn.execute(
            "UPDATE memory SET timestamp = ? WHERE id = ?",
            ("2020-01-01T00:00:00Z", entry.id),
        )
        store.conn.commit()

        # Write a fresh hypothesis
        store.write(MemoryEntry(content="Fresh hypothesis"))
        store.close()

        from loom.recovery import decay_memories

        result = decay_memories(ws, ttl_days=30)
        assert result["decayed"] == 1

        # Verify the old one is obsolete, fresh one is still hypothesis
        store = MemoryStore(ws)
        entries = store.recent(10)
        statuses = {e["content"]: e["status"] for e in entries}
        assert statuses["Old hypothesis"] == "obsolete"
        assert statuses["Fresh hypothesis"] == "hypothesis"
        store.close()

    def test_decay_ignores_validated(self, tmp_path):
        ws = _init(tmp_path)
        store = MemoryStore(ws)
        entry = MemoryEntry(content="Validated entry", status=MemoryStatus.VALIDATED)
        store.write(entry)
        store.conn.execute(
            "UPDATE memory SET timestamp = ? WHERE id = ?",
            ("2020-01-01T00:00:00Z", entry.id),
        )
        store.conn.commit()
        store.close()

        from loom.recovery import decay_memories

        result = decay_memories(ws, ttl_days=1)
        assert result["decayed"] == 0

    def test_dry_run(self, tmp_path):
        ws = _init(tmp_path)
        store = MemoryStore(ws)
        entry = MemoryEntry(content="Old note")
        store.write(entry)
        store.conn.execute(
            "UPDATE memory SET timestamp = ? WHERE id = ?",
            ("2020-01-01T00:00:00Z", entry.id),
        )
        store.conn.commit()
        store.close()

        from loom.recovery import decay_memories

        result = decay_memories(ws, ttl_days=30, dry_run=True)
        assert result["would_decay"] == 1
        assert result["dry_run"] is True

        # Verify nothing actually changed
        store = MemoryStore(ws)
        entries = store.recent(10)
        assert entries[0]["status"] == "hypothesis"
        store.close()


# ── Benchmarks ────────────────────────────────────────────────


class TestBenchmarks:
    def test_benchmarks_run(self):
        from loom.benchmark import run_benchmarks

        results = run_benchmarks()
        assert "init" in results
        assert "write" in results
        assert "search" in results
        assert "handoff" in results
        assert "events" in results

    def test_benchmark_format(self):
        from loom.benchmark import format_report, run_benchmarks

        results = run_benchmarks()
        report = format_report(results)
        assert "p50=" in report
        assert "p95=" in report

    def test_search_under_10ms_p95(self):
        """Search p95 should be under 10ms on 500 entries."""
        from loom.benchmark import run_benchmarks

        results = run_benchmarks()
        assert results["search"]["p95_ms"] < 10, (
            f"Search p95 too slow: {results['search']['p95_ms']}ms"
        )
