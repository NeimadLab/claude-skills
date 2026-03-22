# Architecture

## The Principle: Contract, Not Recipe

PISA defines **what** to produce (contracts), not **how** to produce it (strategies). This single principle enables every form of modularity in the system.

The core contract: given a slide, produce a **V2.1 template JSON** with intent, layout, components (each with role, position, kpi data, visual treatment), semantic groups, reading order, and quality score.

Two extraction strategies fulfil this contract:

- **Strategy 1 — XML Parsing** (python-pptx + extract_engine.py): precise coordinates, batch-capable, works on PPTX files
- **Strategy 2 — Vision** (Claude's native vision): works on images, PDFs, screenshots — anything Claude can see

Both produce identical template JSON. Everything downstream works identically regardless of which strategy created the template.

## Four Independent Layers

```
CANVAS      Skeleton — what components, where        (internal authoring artifact)
    ×
STYLE       Visual personality — accents, spacing    (bold / minimal / gradient / split / photo)
    =
TEMPLATE    The browsable artifact in packs          (canvas + style pre-combined)
    ×
THEME       Brand palette — colors, fonts            (corporate dark / finance dark)
    ×
PERSONA     Communication density                    (executive / strategy / keynote)
    ×
CONTENT     What the slide says                      (user's data)
    =
FINAL SLIDE Rendered PPTX
```

The first two layers (canvas × style) are combined at **authoring time** to produce templates. The remaining layers are applied at **render time**. Users interact with templates — they never see raw canvases.
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
(XML/Vision) (Template→PPTX) (QA+Rubric)
  │            │                │
  └────────────┼────────────────┘
               │
         ┌─────▼─────┐
         │ Template  │  The universal contract
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

- **Templates are portable**: extract from one deck, use in another, share across teams
- **Themes are universal**: any theme works with any template
- **Personas are orthogonal**: a persona changes density and narrative, not structure
- **Packs are composable**: install multiple packs, they merge into one library
- **Strategies are pluggable**: add a new extraction strategy without changing the contract
