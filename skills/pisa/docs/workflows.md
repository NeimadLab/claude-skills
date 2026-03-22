# Workflows A–F

PISA detects which workflow to run based on the user's request.

## Workflow A — Analyze & Extract

**Triggers:** "analyze this deck", "extract canvases", upload PPTX/PDF/image

1. Detect input type (PPTX → Strategy 1, image/PDF → Strategy 2)
2. Extract design system (colors, fonts → theme tokens)
3. For each slide: classify intent, map components, assign roles, estimate positions
4. Build V2.1 canvas JSON with `kpi{}`, `visual{}`, `content_data{}`
5. Generate SVG preview per canvas
6. Present results with quality scores

**Two-pass extraction** for complex slides:
- Pass 1: Zone detection (identify distinct content regions)
- Pass 2: Per-zone component extraction

## Workflow B — Generate

**Triggers:** "create a deck about...", "build 10 slides on..."

1. Detect persona (explicit or inferred from context)
2. Plan slide sequence (narrative arc based on persona)
3. For each slide: resolve the best canvas using priority order:
   - **LOCAL** (extracted from user's deck) → highest priority
   - **OVERRIDE** (user-modified registry canvas) → second
   - **REGISTRY** (installed from packs) → fallback
4. Fill canvas with user content, enforce density limits
5. Resolve theme tokens → concrete values
6. Render via pptxgenjs → PPTX file
7. Run programmatic QA
8. Deliver + offer library export

## Workflow C — Retheme

**Triggers:** "retheme to dark mode", "apply the finance theme"

1. Load the target theme JSON
2. Walk all canvases in the deck
3. Re-resolve all token references against the new theme
4. Re-render → new PPTX with same content, different appearance

## Workflow D — Review

**Triggers:** "review this deck", "score these slides"

1. Load the deck (PPTX → programmatic checks, image → vision review)
2. Run 10 programmatic QA checks
3. Run vision-based review (clarity, hierarchy, data presentation)
4. Score each slide on 5-dimension rubric
5. Generate report with per-slide issues and deck-level summary

## Workflow E — Library & Catalog

**Triggers:** "show my canvases", "browse KPI layouts", "export library"

- **Browse:** Filter by intent/quality/layout → SVG grid via show_widget
- **Preview:** Compare same canvas across themes (side-by-side SVG)
- **Import:** Upload pisa_library.json → restore full session library
- **Export:** "Export my library" → downloadable JSON
- **Details:** "Show canvas X" → SVG + full metadata

## Workflow F — Registry

**Triggers:** "install the finance pack", "list available packs", "check for updates"

PISA ships with a built-in registry URL — no user setup required. To use a custom registry, say: "Use registry at https://..."

- **List:** Fetch registry.json → display available packs/themes/personas
- **Install pack:** Fetch pack JSON → merge canvases (tagged `origin: "registry"`) into session library
- **Install theme:** Fetch theme JSON → set as active theme
- **Install persona:** Fetch persona JSON → apply rules to generation
- **Update:** Compare installed versions with registry → offer to re-fetch
