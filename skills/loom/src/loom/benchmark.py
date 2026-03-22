"""Benchmark suite — measure Loom performance.

Reports init time, search latency (p50/p95/p99), handoff generation,
memory write throughput, and event log throughput.
"""

from __future__ import annotations

import statistics
import tempfile
import time
from pathlib import Path


def run_benchmarks(workspace: Path | None = None) -> dict:
    """Run the full benchmark suite. Returns structured results."""
    results = {}

    results["init"] = _bench_init()
    results["write"] = _bench_write()
    results["search"] = _bench_search()
    results["handoff"] = _bench_handoff()
    results["events"] = _bench_events()

    return results


def _bench_init() -> dict:
    """Benchmark workspace initialization."""
    times = []
    for _ in range(5):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            (root / "pyproject.toml").write_text("[project]\nname='bench'\n")

            from loom.constants import ensure_loom_dir
            from loom.memory import MemoryStore
            from loom.runtime import compute_identity, save_identity

            t0 = time.perf_counter()
            ensure_loom_dir(root)
            store = MemoryStore(root)
            identity = compute_identity(root)
            save_identity(identity, root)
            store.close()
            times.append(time.perf_counter() - t0)

    return _summarize(times, "init (cold start)")


def _bench_write() -> dict:
    """Benchmark memory write throughput."""
    with tempfile.TemporaryDirectory() as td:
        root = Path(td)
        (root / ".loom").mkdir()

        from loom.memory import MemoryStore
        from loom.models import MemoryEntry, MemoryType

        store = MemoryStore(root)
        times = []

        for i in range(100):
            entry = MemoryEntry(
                content=f"Benchmark decision #{i}: use technology-{i} for component-{i}",
                type=MemoryType.DECISION,
                rationale=f"Rationale for decision {i}",
                actor="benchmark",
                tags=[f"tag-{i % 10}", "benchmark"],
            )
            t0 = time.perf_counter()
            store.write(entry)
            times.append(time.perf_counter() - t0)

        store.close()

    return _summarize(times, "write (100 entries)")


def _bench_search() -> dict:
    """Benchmark FTS5 search latency."""
    with tempfile.TemporaryDirectory() as td:
        root = Path(td)
        (root / ".loom").mkdir()

        from loom.memory import MemoryStore
        from loom.models import MemoryEntry, MemoryType

        store = MemoryStore(root)

        # Populate with 500 entries
        words = [
            "FastAPI",
            "PostgreSQL",
            "Redis",
            "JWT",
            "Docker",
            "Kubernetes",
            "GraphQL",
            "WebSocket",
            "OAuth",
            "Terraform",
        ]
        for i in range(500):
            store.write(
                MemoryEntry(
                    content=f"Decision about {words[i % len(words)]}: config-{i}",
                    type=MemoryType.DECISION,
                    tags=[words[i % len(words)].lower()],
                )
            )

        # Search
        times = []
        queries = [
            "FastAPI",
            "PostgreSQL",
            "Redis",
            "JWT",
            "Docker",
            "authentication",
            "database",
            "caching",
            "config",
            "deploy",
        ]
        for q in queries * 10:
            t0 = time.perf_counter()
            store.search(q, limit=10)
            times.append(time.perf_counter() - t0)

        store.close()

    return _summarize(times, "search (100 queries, 500 entries)")


def _bench_handoff() -> dict:
    """Benchmark handoff summary generation."""
    with tempfile.TemporaryDirectory() as td:
        root = Path(td)
        (root / ".loom").mkdir()
        (root / "pyproject.toml").write_text("[project]\n")

        from loom.mcp_server import handle_get_handoff_summary
        from loom.memory import MemoryStore
        from loom.models import MemoryEntry, MemoryType
        from loom.runtime import compute_identity, save_identity

        identity = compute_identity(root)
        save_identity(identity, root)

        store = MemoryStore(root)
        for i in range(50):
            t = [MemoryType.DECISION, MemoryType.GOAL, MemoryType.RISK][i % 3]
            store.write(MemoryEntry(content=f"Entry {i} for handoff", type=t))

        times = []
        for _ in range(20):
            t0 = time.perf_counter()
            handle_get_handoff_summary(store, {"depth": "full"})
            times.append(time.perf_counter() - t0)

        store.close()

    return _summarize(times, "handoff summary (50 entries)")


def _bench_events() -> dict:
    """Benchmark event log write throughput."""
    with tempfile.TemporaryDirectory() as td:
        root = Path(td)
        (root / ".loom").mkdir()

        from loom.events import emit
        from loom.models import Event

        times = []
        for i in range(100):
            t0 = time.perf_counter()
            emit(
                Event(
                    event_type="benchmark_event",
                    actor="benchmark",
                    data={"iteration": i},
                ),
                root,
            )
            times.append(time.perf_counter() - t0)

    return _summarize(times, "event emit (100 events)")


def _summarize(times: list[float], label: str) -> dict:
    """Create a percentile summary from a list of durations."""
    times_ms = [t * 1000 for t in times]
    sorted_ms = sorted(times_ms)
    n = len(sorted_ms)

    return {
        "label": label,
        "count": n,
        "min_ms": round(sorted_ms[0], 2),
        "p50_ms": round(sorted_ms[n // 2], 2),
        "p95_ms": round(sorted_ms[int(n * 0.95)], 2),
        "p99_ms": round(sorted_ms[int(n * 0.99)], 2),
        "max_ms": round(sorted_ms[-1], 2),
        "mean_ms": round(statistics.mean(times_ms), 2),
        "total_ms": round(sum(times_ms), 2),
    }


def format_report(results: dict) -> str:
    """Format benchmark results as a readable report."""
    lines = ["Loom Benchmark Report", "=" * 50, ""]

    for _key, data in results.items():
        lines.append(f"  {data['label']}")
        lines.append(
            f"    p50={data['p50_ms']:.1f}ms  "
            f"p95={data['p95_ms']:.1f}ms  "
            f"p99={data['p99_ms']:.1f}ms  "
            f"mean={data['mean_ms']:.1f}ms  "
            f"(n={data['count']})"
        )
        lines.append("")

    return "\n".join(lines)
