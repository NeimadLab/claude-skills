# Runtime Model

## Overview

The runtime model ensures that a developer can close their laptop, come back the next day, and resume work without rebuilding the world. It manages container lifecycle, cache persistence, environment identity, and health verification.

## Runtime Identity

A deterministic hash computed from the project's environment definition:

| Input | Source | Example |
|-------|--------|---------|
| Container config | `devcontainer.json` | Base image, features, mounts |
| Language lockfiles | `package-lock.json`, `poetry.lock`, `Cargo.lock`, `go.sum` | Exact dependency versions |
| Tool versions | `.tool-versions`, `.nvmrc`, `.python-version` | Runtime versions |
| Base image digest | Docker image SHA | Exact OS + system deps |

The identity is a SHA-256 hash of these inputs, stored in `.loom/runtime.json`. When `loom resume` runs, it recomputes the identity and compares against the stored value.

### Drift Detection

| Drift Level | Trigger | Action |
|-------------|---------|--------|
| **None** | Identity matches | Fast resume from cached volumes |
| **Minor** | Lockfile changed but base image same | Warn + reinstall deps from lockfile |
| **Major** | Base image or language version changed | Suggest `loom repair` or `loom init --force` |
| **Corrupt** | `.loom/runtime.json` missing or invalid | Rebuild from scratch |

## Persistence Strategy

Loom persists the expensive parts of the environment — package caches, build artifacts, and compiled dependencies — in named Docker volumes that survive container rebuilds.

| What | Storage | Survives |
|------|---------|----------|
| Package caches (pip, npm, cargo) | Named Docker volumes | Container rebuild, reboot |
| Build artifacts | Named Docker volumes | Container rebuild, reboot |
| Runtime manifest | `.loom/runtime.json` (in repo) | Git commit |
| Environment snapshot | `.loom/snapshot.json` | Session restart |
| Container image layers | Docker image cache | Until pruned |

Volume names are scoped per project and runtime identity to avoid cross-contamination: `loom-pip-cache-{project_hash}`, `loom-npm-cache-{project_hash}`.

## DevContainer Integration

Loom generates and maintains a `devcontainer.json` that includes:

- **Cache volume mounts** for the detected language ecosystem (pip, npm, cargo, go modules)
- **Loom CLI pre-installed** via a DevContainer feature or postCreateCommand
- **MCP server auto-started** via postStartCommand
- **`.loom/` directory** persisted across container rebuilds

The generated config works with VS Code, Cursor, JetBrains Gateway, and the standalone `devcontainer` CLI.

## Resume Flow

```
loom resume
  ├── Read .loom/runtime.json (stored identity)
  ├── Recompute runtime identity from live environment
  ├── Compare stored vs live
  │   ├── Match → restore caches from named volumes (fast path, <10s)
  │   ├── Minor drift → warn + selective reinstall from lockfiles
  │   └── Major drift → suggest repair or reinit
  ├── Refresh inventory (scan filesystem, update SQLite index)
  ├── Validate event log integrity
  └── Emit resume_completed event with: duration, drift_level, restored_caches
```

## Doctor Flow

```
loom doctor
  ├── Check runtime identity consistency
  ├── Verify lockfile integrity (no uncommitted changes)
  ├── Check Docker daemon availability
  ├── Verify named volumes exist and are accessible
  ├── Check .loom/ directory structure and permissions
  ├── Validate SQLite databases (memory.db, inventory.db)
  ├── Check event log for corruption
  ├── Report disk space for volumes and workspace
  └── Output: JSON diagnostics + human-readable summary + exit code
```

Exit codes: 0 = healthy, 1 = warnings (degraded but functional), 2 = errors (needs repair).
