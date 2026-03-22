"""Runtime identity computation and persistence."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

from loom.constants import (
    LOCKFILES,
    RUNTIME_MANIFEST,
    SUPPORTED_PROJECTS,
    loom_dir,
)
from loom.models import RuntimeIdentity


def detect_project_type(workspace: Path | None = None) -> str | None:
    """Detect the project type from marker files."""
    root = workspace or Path.cwd()
    for ptype, markers in SUPPORTED_PROJECTS.items():
        for marker in markers:
            if (root / marker).exists():
                return ptype
    return None


def _hash_file(path: Path) -> str:
    """SHA-256 hash of a file."""
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(8192), b""):
            h.update(chunk)
    return h.hexdigest()[:16]


def _detect_tool_versions(workspace: Path | None = None) -> dict[str, str]:
    """Read tool version files."""
    root = workspace or Path.cwd()
    versions = {}
    for name in [".tool-versions", ".nvmrc", ".python-version", ".node-version", ".ruby-version"]:
        path = root / name
        if path.exists():
            versions[name] = path.read_text().strip()[:100]
    return versions


def compute_identity(workspace: Path | None = None) -> RuntimeIdentity:
    """Compute deterministic runtime identity from project files."""
    root = workspace or Path.cwd()
    ptype = detect_project_type(root) or "unknown"

    # Hash lockfiles
    lockfile_hashes = {}
    for lf_name in LOCKFILES.get(ptype, []):
        lf_path = root / lf_name
        if lf_path.exists():
            lockfile_hashes[lf_name] = _hash_file(lf_path)

    # Detect tool versions
    tool_versions = _detect_tool_versions(root)

    # Hash devcontainer.json if present
    dc = root / ".devcontainer" / "devcontainer.json"
    if not dc.exists():
        dc = root / "devcontainer.json"
    if dc.exists():
        lockfile_hashes["devcontainer.json"] = _hash_file(dc)

    # Compute composite identity hash
    identity_input = json.dumps(
        {
            "project_type": ptype,
            "lockfiles": lockfile_hashes,
            "tools": tool_versions,
        },
        sort_keys=True,
    )
    identity_hash = hashlib.sha256(identity_input.encode()).hexdigest()[:24]

    return RuntimeIdentity(
        project_type=ptype,
        lockfile_hashes=lockfile_hashes,
        tool_versions=tool_versions,
        identity_hash=identity_hash,
    )


def save_identity(identity: RuntimeIdentity, workspace: Path | None = None) -> Path:
    """Save runtime identity to .loom/runtime.json."""
    from dataclasses import asdict

    path = loom_dir(workspace) / RUNTIME_MANIFEST
    path.write_text(json.dumps(asdict(identity), indent=2) + "\n")
    return path


def load_identity(workspace: Path | None = None) -> RuntimeIdentity | None:
    """Load stored runtime identity."""
    from dataclasses import fields

    path = loom_dir(workspace) / RUNTIME_MANIFEST
    if not path.exists():
        return None
    data = json.loads(path.read_text())
    return RuntimeIdentity(**{f.name: data.get(f.name) for f in fields(RuntimeIdentity)})
