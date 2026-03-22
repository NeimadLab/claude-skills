"""Docker volume management for cache persistence."""

from __future__ import annotations

import json
import subprocess
from pathlib import Path

from loom.constants import CACHE_VOLUME_PATHS, loom_dir
from loom.events import emit
from loom.models import Event
from loom.runtime import detect_project_type, load_identity


def _docker_available() -> bool:
    """Check if Docker daemon is running."""
    try:
        r = subprocess.run(["docker", "info"], capture_output=True, timeout=5)
        return r.returncode == 0
    except (FileNotFoundError, subprocess.TimeoutExpired):
        return False


def _volume_name(workspace: Path, cache_type: str) -> str:
    """Generate a deterministic volume name for a workspace cache."""
    identity = load_identity(workspace)
    project_hash = identity.identity_hash[:12] if identity else "unknown"
    workspace_name = workspace.name.lower().replace(" ", "-")[:20]
    return f"loom-{workspace_name}-{cache_type}-{project_hash}"


def _volume_exists(name: str) -> bool:
    """Check if a Docker volume exists."""
    r = subprocess.run(
        ["docker", "volume", "inspect", name],
        capture_output=True,
    )
    return r.returncode == 0


def _create_volume(name: str) -> bool:
    """Create a Docker volume."""
    r = subprocess.run(
        ["docker", "volume", "create", name],
        capture_output=True,
    )
    return r.returncode == 0


def get_cache_config(workspace: Path | None = None) -> dict[str, list[str]]:
    """Get cache paths for the detected project type."""
    root = workspace or Path.cwd()
    ptype = detect_project_type(root)
    if not ptype:
        return {}
    return {ptype: CACHE_VOLUME_PATHS.get(ptype, [])}


def snapshot_caches(workspace: Path | None = None) -> dict:
    """Snapshot current cache state: which volumes exist, what sizes."""
    root = workspace or Path.cwd()
    if not _docker_available():
        return {"docker": False, "volumes": []}

    caches = get_cache_config(root)
    volumes = []

    for ptype, paths in caches.items():
        for cache_path in paths:
            vol_name = _volume_name(root, cache_path.split("/")[-1])
            exists = _volume_exists(vol_name)
            volumes.append(
                {
                    "name": vol_name,
                    "path": cache_path,
                    "project_type": ptype,
                    "exists": exists,
                }
            )

    snapshot = {"docker": True, "volumes": volumes}

    # Save snapshot
    snap_path = loom_dir(root) / "cache_snapshot.json"
    snap_path.write_text(json.dumps(snapshot, indent=2) + "\n")

    return snapshot


def ensure_volumes(workspace: Path | None = None) -> list[dict]:
    """Ensure Docker volumes exist for all project caches. Create if missing."""
    root = workspace or Path.cwd()
    if not _docker_available():
        return []

    caches = get_cache_config(root)
    results = []

    for _ptype, paths in caches.items():
        for cache_path in paths:
            vol_name = _volume_name(root, cache_path.split("/")[-1])
            existed = _volume_exists(vol_name)

            if not existed:
                created = _create_volume(vol_name)
                results.append(
                    {
                        "name": vol_name,
                        "path": cache_path,
                        "action": "created" if created else "failed",
                    }
                )
            else:
                results.append(
                    {
                        "name": vol_name,
                        "path": cache_path,
                        "action": "exists",
                    }
                )

    return results


def restore_caches(workspace: Path | None = None) -> dict:
    """Restore workspace caches from Docker volumes. Returns restore report."""
    root = workspace or Path.cwd()
    report = {
        "docker_available": _docker_available(),
        "volumes_checked": 0,
        "volumes_restored": 0,
        "volumes_created": 0,
        "details": [],
    }

    if not report["docker_available"]:
        report["details"].append({"status": "skip", "reason": "Docker not available"})
        return report

    results = ensure_volumes(root)
    report["volumes_checked"] = len(results)

    for vol in results:
        if vol["action"] == "created":
            report["volumes_created"] += 1
        elif vol["action"] == "exists":
            report["volumes_restored"] += 1
        report["details"].append(vol)

    # Save snapshot after restore
    snapshot_caches(root)

    emit(
        Event(
            event_type="caches_restored",
            data={
                "checked": report["volumes_checked"],
                "restored": report["volumes_restored"],
                "created": report["volumes_created"],
            },
        ),
        root,
    )

    return report


def generate_devcontainer(workspace: Path | None = None) -> Path:
    """Generate a devcontainer.json with Loom cache volumes."""
    root = workspace or Path.cwd()
    ptype = detect_project_type(root) or "python"
    caches = CACHE_VOLUME_PATHS.get(ptype, [])

    mounts = []
    for cache_path in caches:
        vol_name = _volume_name(root, cache_path.split("/")[-1])
        target = cache_path.replace("~", "/home/vscode")
        mounts.append(f"source={vol_name},target={target},type=volume")

    config = {
        "name": f"Loom: {root.name}",
        "image": "mcr.microsoft.com/devcontainers/base:ubuntu",
        "features": {},
        "mounts": mounts,
        "postCreateCommand": "pip install loom || true",
        "postStartCommand": "loom resume || loom init",
        "customizations": {"vscode": {"extensions": []}},
    }

    # Add language-specific features
    if ptype == "python":
        config["features"]["ghcr.io/devcontainers/features/python:1"] = {"version": "3.12"}
    elif ptype == "node":
        config["features"]["ghcr.io/devcontainers/features/node:1"] = {"version": "20"}
    elif ptype == "rust":
        config["features"]["ghcr.io/devcontainers/features/rust:1"] = {}
    elif ptype == "go":
        config["features"]["ghcr.io/devcontainers/features/go:1"] = {}

    dc_dir = root / ".devcontainer"
    dc_dir.mkdir(exist_ok=True)
    dc_path = dc_dir / "devcontainer.json"
    dc_path.write_text(json.dumps(config, indent=2) + "\n")

    emit(
        Event(
            event_type="devcontainer_generated",
            data={"project_type": ptype, "mounts": len(mounts)},
        ),
        root,
    )

    return dc_path
