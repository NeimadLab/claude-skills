---
layout: default
title: Creating a Skill
---

# Creating a New Claude Skill

## Minimal Skill

Create a folder under `skills/` with one file:

```
skills/my-skill/
└── SKILL.md
```

The SKILL.md should contain:
- **Triggers**: when should Claude activate this skill?
- **Workflows**: what are the named workflows (e.g., A = analyze, B = generate)?
- **Contracts**: what data formats does the skill produce and consume?
- **Quality rules**: what checks ensure good output?

## Recommended Structure

```
skills/my-skill/
├── SKILL.md              ← Required
├── README.md             ← What it does, how to use it
├── CHANGELOG.md          ← Version history
├── CONTRIBUTING.md       ← Skill-specific rules
├── services/             ← Python/JS utilities
├── references/           ← Schemas, specifications
├── registry/             ← Distributable content (optional)
└── examples/             ← Working examples
```

## Key Principles

1. **Self-contained**: everything the skill needs lives in its folder
2. **No shared state**: skills don't reference each other's files
3. **Contract-based**: define what to produce, not how — let Claude choose the strategy
4. **Quality-enforced**: automated checks catch issues before delivery

## CI Integration

The CI workflow automatically discovers new skills by scanning `skills/*/`. It validates:
- SKILL.md exists
- All Python files compile
- All JSON files parse
- Registry (if present) is internally consistent

No CI changes needed when adding a new skill.

## Submitting

1. Create your skill in `skills/my-skill/`
2. Test it in a Claude Project
3. Open a PR — CI validates automatically
