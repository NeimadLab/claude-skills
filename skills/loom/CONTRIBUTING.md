# Contributing to Loom

Thank you for your interest in contributing. Loom is built in the open and welcomes contributions at every level.

## Contribution Paths

### Report a Bug
Open an issue using the **Bug Report** template. Include: Loom version, OS, steps to reproduce, expected vs actual behavior.

### Propose a Feature
Start a [Discussion](../../discussions) describing the problem, proposed solution, and which roadmap phase it fits. If there's consensus, an RFC may be created.

### Improve Documentation
Improvements to `docs/`, root-level files, or inline code comments are always welcome. No RFC required.

### Contribute Code
1. Check [ROADMAP.md](ROADMAP.md) for current priorities
2. Read the relevant docs in `docs/` (architecture, memory-model, etc.)
3. Open an issue or claim an existing one before starting significant work
4. See [Code Standards](#code-standards) below

## Code Standards

- **Python:** ruff for linting + formatting. Type hints everywhere. Docstrings on public functions.
- **SQL:** Lowercase keywords, snake_case names, parameterized queries.
- **JSON:** 2-space indent, valid and parseable.
- **YAML:** 2-space indent, yamllint-clean.
- **Markdown:** ATX headings, fenced code blocks, no trailing whitespace.

## Commit Messages

```
feat(memory): add FTS5 search for decisions
fix(gateway): correct session lease expiration
docs: update architecture diagram
test(e2e): add cross-model handoff scenario
chore(ci): add contract test job
```

Prefix with the subsystem name when the change is subsystem-specific.

## Pull Request Process

1. Fork → branch (`feat/description` or `fix/description`) → make changes → open PR
2. CI validates automatically (lint, unit, integration, contract tests)
3. Tag your PR with the relevant area: `[memory]`, `[gateway]`, `[cli]`, etc.
4. A maintainer reviews and provides feedback
5. Squash merge into main

## RFC Process

RFCs are required for changes to:
- Runtime identity computation
- Memory schema or status model
- MCP tool contracts (public API)
- Gateway semantics or policy model
- Security model

Create a file in `rfcs/` using the template. Comment period: 7 days minimum.

## Architecture Decision Records (ADRs)

Core decisions that contributors must not quietly bypass are recorded in `adrs/`. Use the template in `adrs/template.md`.
