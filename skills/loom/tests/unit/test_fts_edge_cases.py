"""Tests for FTS5 edge cases — special characters, unicode, etc."""

import pytest

from loom.memory import MemoryStore
from loom.models import MemoryEntry


@pytest.fixture
def store(tmp_path):
    (tmp_path / ".loom").mkdir()
    s = MemoryStore(tmp_path)
    yield s
    s.close()


def test_search_special_chars_cpp(store):
    """FTS5 should not crash on C++ style queries."""
    store.write(MemoryEntry(content="Use C++ for the parser engine"))
    results = store.search("C++")
    assert len(results) >= 1
    assert "C++" in results[0]["content"]


def test_search_special_chars_at_sign(store):
    """FTS5 should handle @ symbols."""
    store.write(MemoryEntry(content="Contact admin@example.com for access"))
    results = store.search("admin@example.com")
    assert len(results) >= 1


def test_search_special_chars_dots(store):
    """FTS5 should handle dotted names like node.js."""
    store.write(MemoryEntry(content="Use node.js for the server"))
    results = store.search("node.js")
    assert len(results) >= 1


def test_search_unicode(store):
    """FTS5 should handle unicode content."""
    store.write(MemoryEntry(content="API returns données formatées en UTF-8"))
    results = store.search("données")
    assert len(results) >= 1


def test_search_empty_query(store):
    """Empty query should return empty results, not crash."""
    results = store.search("")
    assert isinstance(results, list)


def test_search_only_special_chars(store):
    """Query of only special chars should not crash."""
    store.write(MemoryEntry(content="Test content"))
    results = store.search("+++---***")
    assert isinstance(results, list)  # No crash = pass


def test_search_quotes(store):
    """Quotes in search should not crash FTS5."""
    store.write(MemoryEntry(content='He said "hello world" to the API'))
    results = store.search('"hello"')
    assert isinstance(results, list)
