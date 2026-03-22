# Contributing Code to Loom

This guide covers everything you need to set up a local development environment and submit quality code contributions.

## Prerequisites

- **Python 3.11+** — install via [pyenv](https://github.com/pyenv/pyenv), system package manager, or [python.org](https://www.python.org/downloads/)
- **Git 2.40+**
- **Docker Desktop** (optional — for runtime persistence and E2E tests)
- **SQLite 3.40+** (usually pre-installed on macOS/Linux)

## Local Setup

```bash
# Clone the repo
git clone https://github.com/NeimadLab/loom.git
cd loom

# Install with dev dependencies
make dev
# or: pip install -e ".[dev]"

# Verify everything works
make lint     # ruff check + format
make test     # pytest
loom --version # CLI installed
```

## Project Structure

```
src/loom/
├── __init__.py     ← Version
├── cli.py          ← CLI commands (Click-based: init, resume, doctor, connect, state)
├── mcp_server.py   ← MCP server implementation (6 tools, stdio transport)
├── memory.py       ← SQLite memory layer (FTS5 search, typed records)
├── models.py       ← Data models (MemoryEntry, Event, RuntimeIdentity)
├── events.py       ← Append-only JSONL event log
├── runtime.py      ← Project detection, identity hash, save/load manifest
├── state.py        ← Workspace inspection, doctor health checks
├── constants.py    ← Paths, defaults, supported projects
└── migrations/     ← SQL migration files (001_initial.sql, ...)
```

Each module has clear boundaries. Cross-module calls go through defined interfaces, not direct internal access.

## Code Conventions

### Python
- **Linter:** ruff (replaces flake8 + isort + pyupgrade + more)
- **Formatter:** ruff format (Black-compatible)
- Run `make lint` before every commit — CI will reject violations
- Use type hints everywhere. `from __future__ import annotations` at the top of every file.
- Use `StrEnum` for enumerations (not `str, Enum`)
- Use `dataclasses` for data models, not Pydantic (keep dependencies minimal)
- Error messages must be actionable: say what went wrong AND what to do

### SQL (SQLite)
- Lowercase keywords (`select`, `insert`, `create table`)
- Snake_case for all names
- Always use parameterized queries — never string interpolation
- Migrations in numbered files: `001_initial.sql`, `002_add_sessions.sql`
- Migrations live in `src/loom/migrations/`

### General
- No `TODO` or `FIXME` without a linked issue
- Log at appropriate levels: `debug` for internals, `info` for user-visible, `warn` for recoverable, `error` for failures
- Every public function needs a docstring

## Testing Your Changes

```bash
make test          # All tests
make test-unit     # Unit tests only
pytest tests/unit/test_memory.py -v  # Single file
```

### Writing Tests

- **Unit tests:** in `tests/unit/`, one file per module (test_memory.py, test_runtime.py, test_events.py)
- **Integration tests:** in `tests/integration/` (coming soon)
- **E2E tests:** in `tests/e2e/` (coming soon)
- **Contract tests:** in `tests/contract/` — verify MCP tool call/response schemas (coming soon)
- **Fixtures:** in `tests/fixtures/`, shared test data
- Use `tmp_path` pytest fixture for isolated test directories
- Each test creates its own `.loom/` — never use a shared state

## Pull Request Checklist

Before opening a PR, verify:

- [ ] `make lint` passes (ruff check + ruff format)
- [ ] `make test` passes (all unit tests green)
- [ ] New code has tests (unit at minimum)
- [ ] Public functions have docstrings
- [ ] User-visible changes have a CHANGELOG entry
- [ ] MCP tool surface changes have updated `schemas/`
- [ ] Commit messages follow conventions

## Commit Messages

```
feat(memory): add FTS5 search for decisions
fix(gateway): correct session lease expiration
docs: update architecture diagram
test(e2e): add cross-model handoff scenario
chore(ci): add contract test job
```

## PR Title Format

```
[subsystem] Short description

Examples:
[memory] Add status promotion with audit trail
[gateway] Implement API key authentication
[cli] Add loom connect for Windsurf
[docs] Update architecture diagram
```

## When Is an RFC Required?

If your change touches any of these, write an RFC first:
- Memory schema (new fields, changed types)
- MCP tool surface (new tools, changed parameters, changed responses)
- Runtime identity computation
- Policy engine semantics
- Security model
- Event log schema

Create `rfcs/NNN-title.md` using the template. Minimum 7-day comment period.

## Getting Help

- **Architecture questions:** check `docs/architecture.md` first, then open a Discussion
- **"Is this in scope?":** check `ROADMAP.md`, especially "Not Planned"
- **Stuck on setup:** open an issue, we'll help
