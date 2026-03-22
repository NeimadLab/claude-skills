"""Unit tests for the memory store."""

import pytest

from loom.memory import MemoryStore
from loom.models import MemoryEntry, MemoryStatus, MemoryType


@pytest.fixture
def store(tmp_path):
    """Create a temporary memory store."""
    loom_dir = tmp_path / ".loom"
    loom_dir.mkdir()
    s = MemoryStore(tmp_path)
    yield s
    s.close()


def test_write_and_read(store):
    entry = MemoryEntry(content="Use JWT for authentication", type=MemoryType.DECISION)
    store.write(entry)
    result = store.get(entry.id)
    assert result is not None
    assert result["content"] == "Use JWT for authentication"
    assert result["type"] == "decision"
    assert result["status"] == "hypothesis"


def test_search_fts(store):
    store.write(MemoryEntry(content="Use PostgreSQL for the database", type=MemoryType.DECISION))
    store.write(MemoryEntry(content="Frontend uses React with TypeScript", type=MemoryType.NOTE))
    store.write(MemoryEntry(content="Consider Redis for caching", type=MemoryType.DECISION))

    results = store.search("database")
    assert len(results) >= 1
    assert "PostgreSQL" in results[0]["content"]


def test_search_with_type_filter(store):
    store.write(MemoryEntry(content="Auth decision", type=MemoryType.DECISION))
    store.write(MemoryEntry(content="Auth note", type=MemoryType.NOTE))

    results = store.search("Auth", type_filter="decision")
    assert len(results) == 1
    assert results[0]["type"] == "decision"


def test_count(store):
    assert store.count() == 0
    store.write(MemoryEntry(content="First"))
    store.write(MemoryEntry(content="Second"))
    assert store.count() == 2


def test_recent(store):
    for i in range(5):
        store.write(MemoryEntry(content=f"Entry {i}"))
    recent = store.recent(3)
    assert len(recent) == 3


def test_update_status(store):
    entry = MemoryEntry(content="Hypothesis entry", status=MemoryStatus.HYPOTHESIS)
    store.write(entry)
    store.update_status(entry.id, MemoryStatus.VALIDATED.value)
    result = store.get(entry.id)
    assert result["status"] == "validated"
