# Getting Started with PISA

## What PISA Does

PISA turns Claude into a presentation specialist. Upload any deck — PPTX, PDF, or screenshot — and Claude reverse-engineers every slide into a reusable **primitive**: a JSON object that captures structure, semantics, and visual treatment without any rendering decisions.

Generate new decks by selecting primitives, filling them with content, and rendering to PPTX. Retheme an entire presentation by swapping one JSON file. Review decks against a professional scoring rubric.

The core insight: **content, structure, design, and rendering are independent layers.** Change any layer without touching the others.

## Step 1 — Add the Skill to Claude

Download [`SKILL.md`](../SKILL.md) and add it to any Claude Project as **Project Knowledge**.

That's it. Claude now has PISA expertise — no other setup needed.

## Step 2 — Connect the Registry

Tell Claude:

```
Use my PISA registry at
https://raw.githubusercontent.com/NeimadLab/claude-skills/main/skills/pisa/registry/registry.json
```

## Step 3 — Install a Pack

```
Install the corporate essentials pack
```

→ 24 primitives across 21 intents, loaded in seconds.

## Step 4 — Create Something

```
Create a 10-slide Q3 performance review using the executive persona
```

```
Upload this PDF and extract all slide primitives
```

```
Show me all KPI dashboard layouts in dark and light themes
```

```
Retheme this deck using the finance dark theme
```

## What You Can Do

| Capability | Trigger |
|-----------|---------|
| **Analyze** | Upload PPTX/PDF/image → decompose into primitives |
| **Generate** | "Create a deck about..." → select primitives → render PPTX |
| **Retheme** | "Switch to dark mode" → swap theme JSON → re-render |
| **Review** | "Score this deck" → programmatic QA + rubric |
| **Catalog** | "Show KPI layouts" → SVG previews inline |
| **Registry** | "Install finance pack" → fetch from GitHub |

## Dependencies

Claude installs these automatically in its sandbox:

```bash
pip install python-pptx numpy scipy scikit-learn
npm install pptxgenjs
```

No LibreOffice. No Pillow. No subprocess calls. Everything runs in Claude's environment.
