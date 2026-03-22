# Release Policy

## Versioning

Loom uses semantic versioning from day one, even during the 0.x stage. Public releases make compatibility intent explicit, and pre-releases communicate stability honestly.

| Form | Meaning | Compatibility Promise |
|------|---------|----------------------|
| `0.x.y` | Pre-1.0 public evolution | Core model still moving. Breaking changes documented in CHANGELOG. |
| `x.y.z-alpha.n` | Early validation build | Architecture or interfaces may move quickly. Not for production. |
| `x.y.z-beta.n` | Feature-complete test build | API surface frozen. Collecting feedback. Bug fixes only. |
| `x.y.z-rc.n` | Release candidate | Only critical fixes and documentation updates. |
| `1.x.y+` | Stable public substrate | Compatibility promises are strong. Breaking changes require major version bump. |

## What Counts as Breaking

For Loom, breaking changes are:

- **CLI commands:** renamed, removed, or changed default behavior
- **MCP tool surface:** tool name, parameter schema, or response schema changes
- **Memory schema:** incompatible changes to `.loom/memory.db` structure
- **Event format:** incompatible changes to events.jsonl structure
- **Policy syntax:** incompatible changes to `.loom/policies/*.yaml` format
- **Runtime identity:** changes to the hash computation that invalidate existing manifests

Non-breaking changes: new CLI commands, new MCP tools, new event types, new policy rules, new memory fields with defaults.

## Release Flow

| Stage | Objective | Required Checks | Deliverable |
|-------|-----------|-----------------|-------------|
| **Scope freeze** | Fix what enters the milestone | Roadmap + issue triage complete | Milestone definition |
| **Stabilization** | Reduce defects, sync docs | Core tests green, docs updated | Candidate branch |
| **Release candidate** | Validate exact build | Smoke, upgrade, install tests | RC tag + notes |
| **Public release** | Ship validated build | Artifacts published, changelog final | Release tag |
| **Post-release** | Capture feedback | Issue review, hotfix decision | Postmortem + patch plan |

## Branching Model

Trunk-based development with short-lived feature branches and a protected `main` branch.

- **Feature branches:** `feat/description` or `fix/description`. Lifetime < 1 week.
- **Release branches:** `release/x.y.z`. Created only when stabilization needs isolation from ongoing main work. Lifetime: days, not weeks.
- **Tags:** Every public release gets a Git tag (`v0.1.0`, `v0.1.1`). Tags are the anchor for release notes, benchmarks, and support boundaries.

## Changelog Requirements

Every user-visible change requires a CHANGELOG.md entry. Each entry includes:

- Category: `Added`, `Changed`, `Deprecated`, `Removed`, `Fixed`, `Security`
- One-line description of the change
- Link to the PR or issue

Release notes are generated from CHANGELOG entries and include: what changed, what is experimental, what broke, and what to test.

## Artifact Publishing

- **GitHub Releases:** tagged builds with release notes and binary attachments
- **PyPI:** `pip install loom` for the CLI + MCP server package
- **Docker Hub / GHCR:** container images for remote Loom server
- **Homebrew:** tap formula for macOS installation
