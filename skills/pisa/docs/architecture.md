# Architecture

## The Principle: Contract, Not Recipe

PISA defines **what** to produce (contracts), not **how** to produce it (strategies). This single principle enables every form of modularity in the system.

The core contract: given a slide, produce a **V2.1 canvas JSON** with intent, layout, components (each with role, position, kpi data, visual treatment), semantic groups, reading order, and quality score.

Two extraction strategies fulfil this contract:

- **Strategy 1 — XML Parsing** (python-pptx + extract_engine.py): precise coordinates, batch-capable, works on PPTX files
- **Strategy 2 — Vision** (Claude's native vision): works on images, PDFs, screenshots — anything Claude can see

Both produce identical canvas JSON. Everything downstream works identically regardless of which strategy created the canvas.

## Four Independent Layers

```
CONTENT     What the slide says          (user's data)
    ↓
STRUCTURE   How it's organized           (canvas: intent + components)
    ↓
DESIGN      How it looks                 (theme: colors + fonts + tokens)
    ↓
RENDERING   How it's built               (pptxgenjs or python-pptx)
```

Each layer is swappable:
- **Swap content** → structure and design stay consistent
- **Swap theme** → entire deck changes appearance, content untouched
- **Swap persona** → density and narrative change, layout unchanged
- **Swap renderer** → output format changes, everything else identical

## Component Architecture

```
┌─────────────────────────────────┐
│  Workflow Detection (A–F)       │  What does the user want?
└──────────────┬──────────────────┘
               │
  ┌────────────┼────────────────┐
  │            │                │
  ▼            ▼                ▼
Extraction   Generation      Review
(XML/Vision) (Canvas→PPTX) (QA+Rubric)
  │            │                │
  └────────────┼────────────────┘
               │
         ┌─────▼─────┐
         │ Canvas  │  The universal contract
         │ JSON V2.1  │  Everything produces it
         └─────┬─────┘  Everything consumes it
               │
  ┌────────────┼────────────────┐
  │            │                │
  ▼            ▼                ▼
SVG Preview  Theme Tokens    Registry
(pure string) (JSON swap)    (GitHub fetch)
```

## What Makes It Modular

- **Canvases are portable**: extract from one deck, use in another, share across teams
- **Themes are universal**: any theme works with any canvas
- **Personas are orthogonal**: a persona changes density and narrative, not structure
- **Packs are composable**: install multiple packs, they merge into one library
- **Strategies are pluggable**: add a new extraction strategy without changing the contract
