# Contributing to Claude Skills

Thank you for your interest in contributing. This document covers the general guidelines. For skill-specific rules (e.g., pack quality requirements for PISA), see the CONTRIBUTING.md inside that skill's folder.

## Contribution Paths

### Report a Bug
Open an issue using the **Bug Report** template. Select the affected skill from the dropdown.

### Propose a New Skill
Start a [Discussion](../../discussions) describing what the skill would do, what workflows it enables, and an example conversation. If there's interest, create a `skills/your-skill/SKILL.md` and open a PR.

### Contribute to an Existing Skill
Each skill has its own contribution rules in `skills/<name>/CONTRIBUTING.md`. Read that file first — it covers quality requirements, data formats, and testing procedures specific to the skill.

### Improve Documentation
Improvements to `docs/`, root-level files, or any skill's README are always welcome.

## General Standards

- **Python:** PEP 8 style, type hints where practical
- **JavaScript:** ES6+, plain Node.js (no TypeScript)
- **JSON:** 2-space indent, valid and parseable
- **Markdown:** ATX headings, fenced code blocks

## Commit Messages

```
feat(pisa): add compound intent support
fix(pisa): correct dark mode KPI rendering
docs: update hub README skill table
chore(ci): improve auto-discovery logic
```

Prefix with the skill name when the change is skill-specific.

## Pull Request Process

1. Fork → branch → make changes → open PR
2. CI validates automatically (each skill checked independently)
3. If your change is to a specific skill, tag it in the PR title: `[pisa] Fix SVG renderer`
4. A maintainer reviews and provides feedback
