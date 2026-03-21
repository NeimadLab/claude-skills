<div align="center">

# PISA — Presentation Intelligence & Slide Architecture

**Analyze, generate, retheme, and review professional PowerPoint decks.**

[![Schema](https://img.shields.io/badge/Schema-V2.1-8B5CF6.svg)](references/pisa-schema-v2.1.md)
[![Primitives](https://img.shields.io/badge/Primitives-61-059669.svg)](registry/)
[![Personas](https://img.shields.io/badge/Personas-8-F97316.svg)](registry/personas/)

</div>

---

## The Core Idea

Every professional presentation is built from a small set of reusable patterns: a KPI dashboard with large numbers, a comparison with side-by-side columns, a timeline with milestones. PISA calls these patterns **primitives**.

A primitive captures the **structure** of a slide (what goes where), the **semantics** (what role each element plays), and the **visual treatment** (dark background, icons, separator lines) — without making any rendering decisions. Colors and fonts come from a separate **theme**. Communication density comes from a separate **persona**.

This separation is what makes PISA powerful:

- **Swap the theme** → the entire deck changes appearance
- **Swap the persona** → the entire deck changes communication density
- **Swap the content** → structure and design stay consistent
- **Share primitives** → teams reuse proven layouts across projects

## Quick Start

1. Download [`SKILL.md`](SKILL.md) and add it to a Claude Project
2. Connect the registry:
   ```
   Use my PISA registry at
   https://raw.githubusercontent.com/NeimadLab/claude-skills/main/skills/pisa/registry/registry.json
   ```
3. Install a pack: `"Install the corporate essentials pack"`
4. Create: `"Build a 10-slide Q3 review using the executive persona"`

## What You Can Do

| Capability | How |
|-----------|-----|
| **Analyze any deck** | Upload PPTX, PDF, or screenshot → decompose into V2.1 primitives |
| **Generate slides** | Describe your deck → select primitives → render PPTX |
| **Retheme instantly** | Swap one JSON → entire deck changes appearance |
| **Review and score** | Programmatic QA + 5-dimension rubric |
| **Browse catalog** | SVG previews inline, filter by intent, compare themes |
| **Install from registry** | One command loads a pack from this repo |

## Eight Personas

| Persona | Archetype | Words/Slide | Key Rule |
|---------|-----------|:-----------:|----------|
| `strategy` | McKinsey / BCG | 90 | Insight titles. 40%+ data slides. |
| `executive` | Board / C-Suite | 60 | 4–8 slides. Elevator test. |
| `keynote` | TED / Conference | 25 | One idea per slide. No bullets. |
| `startup` | Seed / Series A | 50 | Problem → Solution → Ask. |
| `technical` | Architecture | 80 | Diagrams first. Monospace for code. |
| `sales` | Pitch / Proposal | 65 | Benefit-led titles. Social proof. |
| `workshop` | Training | 70 | Learning objectives. Numbered steps. |
| `academic` | Conference | 75 | Citations required. Error bars. |

## Schema V2.1

Every slide decomposes into a primitive JSON with:

- **`kpi{}`** — value, unit (superscript/suffix), label, annotation, trend
- **`visual{}`** — bg_variant (dark/light), borders, icon hints, shape
- **`content_data{}`** — timeline entries, org charts, checklists (not flattened to text)
- **`zones[]`** — compound slides with multiple intents mapped to spatial regions

[Full schema reference →](references/pisa-schema-v2.1.md)

## Registry

| Pack | Primitives | Install |
|------|:---------:|---------|
| Corporate Essentials | 24 | `Install corporate essentials` |
| Finance & Reporting | 14 | `Install finance reporting` |
| Strategy Consulting | 12 | `Install strategy consulting` |
| Startup Pitch | 11 | `Install startup pitch` |

3 themes (Corporate Dark, Corporate Light, Finance Dark) and 8 personas available.

## Directory Structure

```
skills/pisa/
├── SKILL.md                ← Drop this into Claude
├── subskills/             ← XML extraction engine
├── services/               ← SVG renderer + QA engine
├── references/             ← Schema, personas, architecture
├── scripts/                ← Bootstrap for Tier 2
├── registry/               ← Packs, themes, personas (Claude fetches these)
└── docs/                   ← Guide + Pages content
```

**Everything is self-contained.** This folder has no dependencies on anything outside it.

## Contributing to PISA

See [CONTRIBUTING.md](CONTRIBUTING.md) for pack quality requirements, theme token specs, and persona format.
