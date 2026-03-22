<div align="center">

# PISA — Presentation Intelligence & Slide Architecture

**Analyze, generate, retheme, and review professional PowerPoint decks.**

[![Schema](https://img.shields.io/badge/Schema-V2.1-8B5CF6.svg)](references/pisa-schema-v2.1.md)
[![Canvases](https://img.shields.io/badge/Canvases-61-059669.svg)](registry/)
[![Personas](https://img.shields.io/badge/Personas-8-F97316.svg)](registry/personas/)
[![Gallery](https://img.shields.io/badge/Gallery-→_Browse_all_canvases-1A5FB4.svg)](docs/gallery.md)

</div>

### Preview — Corporate Essentials Pack (dark theme)

<p align="center">
  <img src="docs/gallery/hero.svg" alt="PISA canvas preview — KPI dashboard, executive summary, process flow, SWOT" width="100%">
</p>

> 61 canvases across 4 packs. Each canvas is a reusable slide structure — fill with your content, style with your theme, shape with your persona. [Browse the full gallery →](docs/gallery.md)

---

## The Core Idea

Every professional presentation is built from a small set of reusable patterns: a KPI dashboard with large numbers, a comparison with side-by-side columns, a timeline with milestones. PISA calls these patterns **canvases**.

A canvas captures the **structure** of a slide (what goes where), the **semantics** (what role each element plays), and the **visual treatment** (dark background, icons, separator lines) — without making any rendering decisions. Colors and fonts come from a separate **theme**. Communication density comes from a separate **persona**.

This separation is what makes PISA powerful:

- **Swap the theme** → the entire deck changes appearance
- **Swap the persona** → the entire deck changes communication density
- **Swap the content** → structure and design stay consistent

---

## Showcase

Every canvas is a reusable slide structure. Install a pack, fill with your content, apply any theme.

**[Browse all 61 canvases →](docs/showcase.md)**

<table><tr>
<td width="33%"><img src="docs/gallery/ce_kpi4.svg" width="100%"><br><sub>KPI Dashboard · dark/light/accent</sub></td>
<td width="33%"><img src="docs/gallery/fin_kpi6.svg" width="100%"><br><sub>Finance KPI Grid · 6 cards</sub></td>
<td width="33%"><img src="docs/gallery/st_kpi6.svg" width="100%"><br><sub>Strategy KPIs · data-rich</sub></td>
</tr><tr>
<td width="33%"><img src="docs/gallery/ce_exec_3c.svg" width="100%"><br><sub>Executive Summary · 3 columns</sub></td>
<td width="33%"><img src="docs/gallery/ce_proc4.svg" width="100%"><br><sub>Process · numbered steps</sub></td>
<td width="33%"><img src="docs/gallery/st_matrix.svg" width="100%"><br><sub>Impact-Effort Matrix</sub></td>
</tr><tr>
<td width="33%"><img src="docs/gallery/pi_traction.svg" width="100%"><br><sub>Startup Traction · KPIs + chart</sub></td>
<td width="33%"><img src="docs/gallery/ce_swot.svg" width="100%"><br><sub>SWOT · colored quadrants</sub></td>
<td width="33%"><img src="docs/gallery/ce_fun.svg" width="100%"><br><sub>Funnel · narrowing stages</sub></td>
</tr></table>
- **Share canvases** → teams reuse proven layouts across projects

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
| **Analyze any deck** | Upload PPTX, PDF, or screenshot → decompose into V2.1 canvases |
| **Generate slides** | Describe your deck → select canvases → render PPTX |
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

Every slide decomposes into a canvas JSON with:

- **`kpi{}`** — value, unit (superscript/suffix), label, annotation, trend
- **`visual{}`** — bg_variant (dark/light), borders, icon hints, shape
- **`content_data{}`** — timeline entries, org charts, checklists (not flattened to text)
- **`zones[]`** — compound slides with multiple intents mapped to spatial regions

[Full schema reference →](references/pisa-schema-v2.1.md)

## Registry

| Pack | Canvases | Install |
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
├── services/
│   ├── extraction/         ← XML parsing engine (python-pptx)
│   ├── svg/                ← SVG canvas preview renderer
│   ├── qa/                 ← Programmatic QA (10 checks)
│   └── generator/          ← Canvas + theme + content → PPTX
├── references/             ← Schema, personas, architecture
├── scripts/                ← Bootstrap for Tier 2
├── registry/               ← Packs, themes, personas (Claude fetches these)
└── docs/                   ← Guide, showcase gallery, Pages content
```

**Everything is self-contained.** This folder has no dependencies on anything outside it.

## Contributing to PISA

See [CONTRIBUTING.md](CONTRIBUTING.md) for pack quality requirements, theme token specs, and persona format.

See [ROADMAP.md](ROADMAP.md) for what's planned and where to contribute.
