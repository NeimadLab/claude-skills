"""Unit tests for runtime identity."""

from loom.runtime import compute_identity, detect_project_type, load_identity, save_identity


def test_detect_python_project(tmp_path):
    (tmp_path / "pyproject.toml").write_text('[project]\nname="test"')
    assert detect_project_type(tmp_path) == "python"


def test_detect_node_project(tmp_path):
    (tmp_path / "package.json").write_text("{}")
    assert detect_project_type(tmp_path) == "node"


def test_detect_unknown(tmp_path):
    assert detect_project_type(tmp_path) is None


def test_identity_deterministic(tmp_path):
    (tmp_path / "package.json").write_text('{"name": "test"}')
    (tmp_path / ".loom").mkdir()
    id1 = compute_identity(tmp_path)
    id2 = compute_identity(tmp_path)
    assert id1.identity_hash == id2.identity_hash


def test_identity_changes_with_lockfile(tmp_path):
    (tmp_path / "package.json").write_text('{"name": "test"}')
    (tmp_path / ".loom").mkdir()

    id1 = compute_identity(tmp_path)

    (tmp_path / "package-lock.json").write_text('{"lockfileVersion": 3}')
    id2 = compute_identity(tmp_path)

    assert id1.identity_hash != id2.identity_hash


def test_save_and_load_identity(tmp_path):
    (tmp_path / ".loom").mkdir()
    (tmp_path / "pyproject.toml").write_text("[project]")
    identity = compute_identity(tmp_path)
    save_identity(identity, tmp_path)
    loaded = load_identity(tmp_path)
    assert loaded is not None
    assert loaded.identity_hash == identity.identity_hash
