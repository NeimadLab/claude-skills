"""Tests for data models."""

import json

from loom.models import Event, MemoryEntry, MemoryStatus, MemoryType, generate_id


def test_generate_id_unique():
    ids = {generate_id() for _ in range(100)}
    assert len(ids) == 100


def test_memory_entry_defaults():
    entry = MemoryEntry(content="Test")
    assert entry.type == MemoryType.NOTE
    assert entry.status == MemoryStatus.HYPOTHESIS
    assert entry.content == "Test"
    assert entry.id  # not empty
    assert entry.timestamp  # not empty


def test_memory_entry_to_dict():
    entry = MemoryEntry(content="Test", type=MemoryType.DECISION)
    d = entry.to_dict()
    assert d["type"] == "decision"
    assert d["status"] == "hypothesis"
    assert isinstance(d["linked_files"], list)


def test_event_to_json():
    event = Event(event_type="test_event", data={"key": "value"})
    j = event.to_json()
    parsed = json.loads(j)
    assert parsed["event_type"] == "test_event"
    assert parsed["data"]["key"] == "value"


def test_valid_transitions():
    from loom.models import VALID_TRANSITIONS

    assert MemoryStatus.VALIDATED in VALID_TRANSITIONS[MemoryStatus.HYPOTHESIS]
    assert MemoryStatus.REJECTED in VALID_TRANSITIONS[MemoryStatus.HYPOTHESIS]
    assert len(VALID_TRANSITIONS[MemoryStatus.OBSOLETE]) == 0
