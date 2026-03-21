<div align="center">

# Claude Skills

**Drop-in expertise modules for Claude — one file, zero infrastructure.**

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)

[What is this?](#what-is-a-claude-skill) · [Available Skills](#available-skills) · [Create Your Own](#creating-a-new-skill) · [Contributing](CONTRIBUTING.md)

</div>

---

## What is a Claude Skill?

A Claude Skill is a structured markdown file you add to a Claude Project. It gives Claude **deep, specialized expertise** — workflows, quality standards, tool orchestration, and domain knowledge — that it applies automatically whenever relevant.

There is nothing to install on your machine. No plugins, no API keys, no containers. Claude reads the file, understands its role, and operates accordingly. One file transforms a general-purpose assistant into a domain expert.

```
┌─────────────────────────────────────┐
│         Claude Project              │
│                                     │
│  📄 SKILL.md  ← You add this       │
│                                     │
│  Claude reads it and gains:         │
│  · Workflow detection & routing     │
│  · Domain-specific quality rules    │
│  · Tool orchestration patterns      │
│  · Data format contracts            │
│                                     │
│  No code runs on your machine.      │
│  Everything executes in Claude's    │
│  sandbox.                           │
└─────────────────────────────────────┘
```

---

## Available Skills

| Skill | Description | Status |
|-------|-------------|:------:|
| **[PISA](skills/pisa/)** | Presentation Intelligence & Slide Architecture — analyze, generate, retheme, and review professional PowerPoint decks | ✅ v1.0 |

> More skills coming. [Suggest one →](../../discussions)

---

## How to Use a Skill

1. Go to the skill's folder (e.g., `skills/pisa/`)
2. Download the `SKILL.md` file
3. Open your Claude Project → add it as **Project Knowledge**
4. Start talking to Claude — the skill activates automatically

Each skill's README has specific instructions, examples, and capabilities.

---

## Creating a New Skill

Every skill lives in its own folder under `skills/`. A minimal skill needs one file:

```
skills/my-skill/
└── SKILL.md
```

A full skill can include anything it needs:

```
skills/my-skill/
├── SKILL.md              ← Required: the file Claude reads
├── README.md             ← Recommended: what the skill does, how to use it
├── CHANGELOG.md          ← Recommended: version history
├── CONTRIBUTING.md       ← Optional: skill-specific contribution rules
├── sub-skills/           ← Optional: specialized sub-modules
├── services/             ← Optional: Python/JS utilities Claude runs
├── references/           ← Optional: data files, schemas, specifications
├── registry/             ← Optional: distributable content (if applicable)
├── examples/             ← Optional: working code examples
└── docs/                 ← Optional: GitHub Pages content
```

**Key principle: each skill is fully self-contained.** Everything Claude needs to understand and operate the skill lives inside its folder. No references to files outside the skill directory. No shared infrastructure to coordinate with.

This means:
- Contributors can work on one skill without touching any other
- CI automatically discovers and validates each skill independently
- Adding a new skill requires **zero edits** to any root-level file

See [docs/creating-a-skill.md](docs/creating-a-skill.md) for a complete guide.

---

## Repository Structure

```
claude-skills/
├── skills/              ← One folder per skill (self-contained)
│   ├── pisa/            ← Presentation Intelligence
│   └── next-skill/      ← Your skill here
├── docs/                ← GitHub Pages hub site
├── .github/             ← CI (auto-discovers skills), issue templates
├── README.md            ← This file
├── CONTRIBUTING.md      ← General contribution guidelines
└── LICENSE              ← MIT
```

---

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md).

**Quick paths:**
- 🐛 Found a bug → [Open an issue](.github/ISSUE_TEMPLATE/bug-report.yml)
- 💡 Have a skill idea → [Start a Discussion](../../discussions)
- 📦 Want to contribute to a specific skill → see that skill's CONTRIBUTING.md
- 🆕 Want to create a new skill → see [Creating a New Skill](docs/creating-a-skill.md)

## License

MIT — see [LICENSE](LICENSE).
