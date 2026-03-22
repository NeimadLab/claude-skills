"""Unit tests for event log."""

from loom.events import count, emit, tail
from loom.models import Event


def test_emit_and_tail(tmp_path):
    (tmp_path / ".loom").mkdir()
    emit(Event(event_type="test_event", data={"key": "value"}), tmp_path)
    events = tail(10, tmp_path)
    assert len(events) == 1
    assert events[0]["event_type"] == "test_event"


def test_count(tmp_path):
    (tmp_path / ".loom").mkdir()
    assert count(tmp_path) == 0
    emit(Event(event_type="a"), tmp_path)
    emit(Event(event_type="b"), tmp_path)
    assert count(tmp_path) == 2
