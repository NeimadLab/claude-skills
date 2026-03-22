# Getting Started with PISA

## What PISA Does

PISA turns Claude into a presentation specialist. It produces professional slides through 4 independent layers:

```
Canvas (skeleton) × Style (personality) = Template (what you browse)
Template × Theme (colors) × Persona (density) × Content = Final Slide
```

Upload any deck → PISA extracts templates. Pick templates → PISA generates PPTX. Swap the theme → entire deck changes palette. Swap the persona → density adapts to your audience.

## Step 1 — Add the Skill to Claude

Download [`SKILL.md`](../SKILL.md) and add it to any Claude Project as **Project Knowledge**.

That's it. Claude now has PISA expertise — no other setup needed.

## Step 2 — Install a Pack

The registry URL is built into SKILL.md — no setup needed. Just say:

```
Install the corporate essentials pack
```

→ 24 templates across 21 intents, loaded in seconds.

## Step 3 — Create Something

```
Create a 10-slide Q3 performance review using the executive persona
```

```
Upload this PDF and extract all slide templates
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
| **Analyze** | Upload PPTX/PDF/image → decompose into templates |
| **Generate** | "Create a deck about..." → select templates → render PPTX |
| **Retheme** | "Switch to dark mode" → swap theme JSON → re-render |
| **Review** | "Score this deck" → programmatic QA + rubric |
| **Catalog** | "Show KPI layouts" → SVG previews inline |
| **Registry** | "Install finance pack" → fetch from GitHub |
| **Local override** | Upload your deck → your templates take priority over registry |

## Dependencies

Claude installs these automatically in its sandbox:

```bash
pip install python-pptx numpy scipy scikit-learn
npm install pptxgenjs
```

No LibreOffice. No Pillow. No subprocess calls. Everything runs in Claude's environment.
