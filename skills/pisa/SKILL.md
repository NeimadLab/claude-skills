---
name: PISA
description: Presentation Intelligence & Slide Architecture — analyze, generate, retheme, and review professional PowerPoint decks
version: 1.0.0
registry: https://raw.githubusercontent.com/NeimadLab/claude-skills/main/skills/pisa/registry/registry.json
---

# PISA — Presentation Intelligence & Slide Architecture

## Trigger

Activate when the user:
- Uploads a PPTX and asks to analyze, review, score, extract, decompose, or reverse engineer it
- Asks to generate, create, build, or draft a PowerPoint, presentation, slide deck, or slides
- Asks to retheme, rebrand, or reskin existing slides or a deck
- Mentions "PISA", "slide templates", "slide library", "design tokens", or "deck persona"
- Asks to install, list, or update PISA packs, themes, styles, or personas
- Uploads a pisa_library.json, .pisa file, or .pisa-collection
- Asks to show the slide catalog or preview templates
- References specific persona names: strategy, executive, keynote, startup, technical, sales, workshop, academic

---

## How PISA Works — The 4-Layer Model

**This section defines the entire system. Read it first.**

Every PISA slide is produced through 4 independent layers:

```
CANVAS  ×  STYLE  =  TEMPLATE              (what you browse & pick)
TEMPLATE  ×  THEME  ×  PERSONA  ×  CONTENT  =  FINAL SLIDE  (what gets rendered)
```

### Layer 1 — Canvas (skeleton)
A canvas defines the **structure** of a slide: what components exist, where they sit, and what role each plays. It has NO visual personality — no colors, no decorative choices, no shadows.

A canvas answers: "This slide has a title at top, 4 KPI cards in a grid, and a body panel below."

Canvases are internal authoring artifacts. Users never see or select them directly.

### Layer 2 — Style (visual personality)
A style defines **how** a canvas looks: card background patterns (dark/light/accent alternation), corner radius, accent bar placement, spacing, shadows, decorative elements. Styles are independent of color — the same style works with any theme.

5 built-in styles: **bold** (geometric accents, high contrast), **minimal** (whitespace, thin borders), **gradient** (color bands, overlays), **split** (two-tone panels), **photo** (image-first).

### Layer 3 — Template (Canvas × Style)
A template is a **canvas with a style pre-applied**. This is the concrete artifact that:
- Lives in packs
- Appears in the gallery / showcase
- Gets selected by Claude during generation
- Gets installed from the registry

**Templates are what users see, browse, and choose.** When someone says "show me cover templates", they see templates — not raw canvases.

### Layer 4 — Theme, Persona, Content (applied at render time)
- **Theme** swaps colors and fonts. Same template, different brand.
- **Persona** controls communication density. Same template, different audience.
- **Content** fills the slots. Same template, different message.

### Why this matters
- Swap the style → the entire deck changes visual feel (bold → minimal)
- Swap the theme → the entire deck changes brand palette (corporate → finance)
- Swap the persona → the entire deck changes density (executive → strategy)
- None of these require new templates

### What's in a pack
Packs contain **templates** (pre-combined canvas + style), organized by domain:
- `corporate-essentials` — 24 templates, 21 intents, general business
- `finance-reporting` — 14 templates, CFO decks, quarterly reviews
- `strategy-consulting` — 12 templates, McKinsey/BCG-style
- `startup-pitch` — 11 templates, seed/Series A pitch decks

Each template includes an SVG preview, intent classification, and quality score.

---

## Two Tiers

**Tier 1 (this file):** Claude-native. Zero local setup. Dependencies installed on the fly.
Library is session-ephemeral (user exports/re-uploads JSON for persistence).
SVG previews displayed inline. Programmatic QA on generated PPTX. No external
rendering dependencies — no LibreOffice, no Pillow.

**Tier 2:** Full local setup via `scripts/bootstrap.sh`. Persistent library, versioning,
FastAPI backend, .pisa exchange. Same engine, same quality. Difference is persistence.

## Environment Setup (run once per session)

```bash
pip install python-pptx numpy scipy scikit-learn --break-system-packages -q
npm install pptxgenjs 2>/dev/null
```

---

## What You Can Do With PISA (Tier 1)

All of these work in Claude's sandbox with zero setup beyond the pip/npm install above.

### Build & Generate
- **"Create a 10-slide Q3 review deck"** → Selects templates from library, fills with content, renders PPTX
- **"Use the executive persona"** → Switches density, title style, narrative to board-level
- **"Retheme this deck to dark mode"** → Swaps theme tokens, re-renders same templates
- **"Review this deck and score it"** → Programmatic + vision QA, 5-dimension rubric

### Analyze & Extract
- **Upload a PPTX** → Reverse-engineers every slide into reusable V2.1 templates
- **Upload a PDF or screenshot** → Vision extraction produces the same template format
- **"What kind of slide is this?"** → Quick vision analysis with intent + layout classification

### Library & Catalog
- **"Show me all KPI templates"** → SVG visual catalog displayed inline via show_widget
- **"Show this in dark and light themes"** → Side-by-side SVG theme comparison
- **"Export my library"** → Downloads pisa_library.json for next session
- **Upload pisa_library.json** → Restores full library from previous session
- **Upload a .pisa-collection ZIP** → Imports shared template collections

### Registry & Packs (Online Catalog)
- **"List available packs"** → Fetches registry.json from GitHub, shows available packs
- **"Install the finance pack"** → web_fetch loads 14 templates + themes into session
- **"Install corporate dark theme"** → Fetches and activates a theme from registry
- **"Check for updates"** → Compares installed vs registry versions, offers to update
- **"Install the keynote persona"** → Loads persona rules from registry

**The registry is live and online. Always fetch it — never say it's unavailable.**

### Styles (Visual Personality)
- **"Use the bold style"** → Geometric accents, high contrast, shadows
- **"Switch to minimal"** → Maximum whitespace, thin borders, no decoration
- **"Show me this slide in all styles"** → Side-by-side comparison of 5 styles
- **"Use gradient for the cover"** → Per-slide style override

### Local Overrides
Templates you extract from your own decks automatically take priority over registry
templates. Your brand, your layouts, your style — always used first.
- **Upload your deck** → Extract → your templates are tagged `local` and used first
- **"I prefer my KPI layout"** → Tags it as `override`, always selected over registry
- **"Use the registry version"** → Forces the pack version for that slide

### Persistence Between Sessions
Library resets between sessions. Three ways to persist:
1. **Export/Import JSON:** End of session → export. Next session → upload the file.
2. **Re-install from registry:** "Install corporate pack" — one command, seconds to load.
3. **Upload .pisa-collection:** Share entire libraries between projects or with colleagues.

---

## Architecture Principle — Contract, Not Recipe

PISA defines WHAT to produce (contracts), not HOW to produce it (strategies).

**The core contract:** Given a slide, produce a V2 template JSON with intent, layout_type,
components (role + position), semantic groups, reading order, and quality score.

**Two strategies fulfil this contract:**
- **Strategy 1 — XML parsing** (python-pptx + extract_engine.py): precise, batch-capable, works on PPTX files
- **Strategy 2 — Vision** (Claude's native image understanding): works on images/screenshots/PDFs, better for visual judgment

Claude chooses the best strategy per situation. Both produce identical output format.
Everything downstream (library, SVG preview, QA, generation, retheme) works the same
regardless of which strategy produced the template.

This design means PISA gets better as models get better — a future model with superior
vision replaces 571 lines of heuristic Python with a single structured prompt.

### Architecture Diagram

When a user asks "how does PISA work?" or needs an overview, display the architecture
SVG from `references/pisa-architecture.svg` via `show_widget`. It shows:

- **Gray (fixed):** Workflow router, V2 template contract, token resolution, renderer
- **Purple (pluggable strategies):** Extraction (XML or Vision), QA (Programmatic or Vision)
- **Teal (pluggable content):** Template packs, themes, personas — all swappable via registry
- **Coral (distribution):** GitHub registry feeds packs/themes/personas via web_fetch

The key insight: everything above and below the "V2 template JSON contract" bar is
independent. Extraction strategies produce templates. Generation consumes templates.
Swap any colored module without touching the others.

---

## Execution Flow

```
User request
    ↓
[1] Detect Workflow:
    A — "analyze/extract/reverse engineer" + PPTX/PDF/image
    B — "create/generate/build" + topic/brief
    C — "retheme/rebrand/reskin" + new theme
    D — "review/score/check" + PPTX/PDF/image
    E — "show library/browse/catalog/export/import" + library actions
    F — "install/list/update" + packs/themes/personas from registry
    ↓
[2] Detect Persona → affects density, titles, narrative, intent selection
    ↓
[3] Install dependencies if not yet done this session
    ↓
[4] Load library (session JSON, or from uploaded file, or install pack from registry)
    ↓
[5] Resolve templates: local > override > registry
    ↓
[6] Execute workflow steps
    ↓
[7] Render → pptxgenjs for PPTX output, SVG for previews via show_widget
    ↓
[8] Programmatic QA → validate PPTX with python-pptx (no LibreOffice)
    ↓
[9] Deliver PPTX + offer library export
```

---

## Resource Resolution — Unified Rules

Every PISA resource (templates, personas, themes, density limits) can come from
multiple sources. The same resolution order applies to ALL resource types:

```
PRIORITY (highest first):

1. LOCAL      — extracted or created by the user this session
2. OVERRIDE   — user modified a registry/built-in resource
3. REGISTRY   — fetched from the online registry via web_fetch
4. BUILT-IN   — hardcoded in this SKILL.md file (fallback only)
```

### How Claude identifies the source

Every resource carries metadata:

| Resource | Source field | Version field |
|----------|-------------|---------------|
| Templates | `source.origin` = local/override/registry | `version` (integer) |
| Personas | `source.origin` = registry/builtin | `version` = "1.1.0" |
| Themes | `_source` = registry/builtin | `_version` = "1.1.0" |
| Density limits | Inherited from active persona | — |

### Rules

- **Templates:** When selecting for an intent, pick the highest-priority origin. Within same origin, pick highest quality_score. `source.pack` identifies which pack it came from.
- **Personas:** If Claude fetches a persona JSON from the registry, its values override the SKILL.md summaries. If the registry is unreachable, use the SKILL.md summaries.
- **Themes:** Pack-embedded themes (inside pack JSONs) and standalone themes (separate JSON files) use the same flat token format. Pack-embedded themes load automatically with the pack. Standalone themes load explicitly ("install corporate dark theme"). User-defined themes override both.
- **Density limits:** Come from the active persona. If no persona is active, use the defaults in the Density Limits table below.

### Conflict detection

When the same resource exists at multiple levels:
- Claude uses the highest-priority version silently (no need to ask)
- If the user says "why are you using this layout?" → explain the resolution chain
- If the user says "use the registry version" → force origin=registry for that resource
- If the user says "use my version" → force origin=local

---

## Workflow F — Registry & Pack Management

### REGISTRY URL — USE THIS EXACT URL:
```
https://raw.githubusercontent.com/NeimadLab/claude-skills/main/skills/pisa/registry/registry.json
```

When the user asks ANYTHING about packs, registry, available templates, or says "list/install/update":
→ IMMEDIATELY `web_fetch` the URL above. Do NOT say it's not live. Do NOT fall back to built-in templates. FETCH FIRST.

### List Available Resources
When user says "list PISA packs" / "what packs are available" / "show registry":
1. `web_fetch("https://raw.githubusercontent.com/NeimadLab/claude-skills/main/skills/pisa/registry/registry.json")`
2. Parse and display available packs, themes, personas with descriptions
3. Show installed vs available versions

### Install a Pack
When user says "install [pack name]" / "load the finance pack":
1. `web_fetch` registry.json (URL above)
2. Find the pack entry, build full URL: `{base_url}/{pack.url}`
3. `web_fetch` the pack JSON (contains templates + embedded SVGs + themes)
4. Merge templates into the session library, tagged `source.origin: "registry"`
5. Load included themes
6. Confirm: "Loaded Finance & Reporting: 14 templates across 8 intents, 2 themes."

### Install a Theme
When user says "install [theme name]" / "use corporate dark theme":
1. `web_fetch` the theme JSON from registry: `{base_url}/themes/{theme_id}.json`
2. Set as active theme for the session

### Install a Persona
When user says "use strategy persona" / "switch to keynote mode":
1. `web_fetch` the persona JSON: `{base_url}/personas/{persona_id}.json`
2. Apply persona rules to all subsequent generation and review operations

### Check for Updates
When user says "check for updates" / "update packs":
1. `web_fetch` registry.json
2. Compare installed pack versions with registry versions
3. Report which packs have updates available
4. Re-fetch updated packs on user confirmation

---

## Persona System

A persona is a generation strategy that controls HOW a deck communicates. It is NOT a theme.
Themes control colours/fonts. Personas control content density, title style, narrative arc,
intent selection, and visual ratio.

### Applying a Persona
When a persona is active, override these defaults for ALL generation and review operations.
See **Resource Resolution** section above for priority rules.

| Parameter | Default | Persona overrides |
|-----------|---------|------------------|
| max_words_body | 75 | persona.density.max_words_body |
| max_bullets | 5 | persona.density.max_bullets |
| title_style | insight | persona.titles.style |
| narrative_framework | none | persona.narrative.framework |
| preferred_intents | all | persona.preferred_intents |
| discouraged_intents | none | persona.discouraged_intents |
| bullets_allowed | yes | persona.visual.bullets_allowed |

### Built-in Persona Summaries

**strategy** (McKinsey/BCG) — High density (90 words). Pyramid narrative. Titles are assertive insights. 40%+ data slides. Source citations required on every data slide.

**executive** (Board / C-Suite) — Low density (60 words). SCR narrative. Max 3 bullets. 4-8 slides total. Action-oriented titles ("Approve APAC expansion").

**keynote** (TED/conference) — Minimal density (25 words). Story arc. Bullets FORBIDDEN. One idea per slide. 90% visual. 20-40 thin slides.

**startup** (Seed/Series A) — Medium density (50 words). Problem→Solution→Ask. 10-15 slides. Traction must show MoM growth. Clear "ask" slide with amount and use of funds.

**technical** (Architecture/sprint) — Medium-high density (80 words). Chronological. Monospace for code. Diagrams first.

**sales** (Pitch/proposal) — Medium density (65 words). Problem→Impact→Proof→CTA. Social proof prominent. Benefit-led titles.

**workshop** (Training) — Medium density (70 words). Progressive disclosure. Numbered steps. Learning objectives per section.

**academic** (Conference/thesis) — Medium density (75 words). Scientific method. Citations on every data slide. Error bars required.

---

## Workflow A — Reverse Engineer

When user uploads a PPTX to analyze or extract:

### A1. Extract design system
```python
from pptx import Presentation
prs = Presentation("uploaded.pptx")
# Walk all slides: extract unique colours from text runs and shape fills
# Extract font names (heading vs body by frequency)
# Map to token anchors: most frequent dark → token.color.primary, etc.
# Present theme JSON to user for validation
```

### A2. Slide Analysis — The Contract (V2.1)

**For each slide, produce a V2.1 template JSON with these fields:**
- `intent` (one of 21 canonical intents) + `intent_confidence` (0–1)
- `secondary_intent` (optional — for compound slides with 2+ intents fused)
- `layout_type` (grid / columns / rows / stacked / radial / freeform)
- `layout_variant` (specific pattern: grid_alternating_dark_light, columns_with_headers, etc.)
- `components[]` — each with: `role`, `x_pct`, `y_pct`, `w_pct`, `h_pct`, `rotation`, plus:
  - `kpi{}` (when role=kpi_card): value, unit, unit_position, label, sub_annotation, trend
  - `visual{}` (any role): bg_variant, border, has_separator, has_icon, icon_hint, shape
  - `content_data{}` (when role=body with internal structure): type, entries[], axis, alternating
- `zones[]` (optional — for compound slides: each zone has its own intent and component indices)
- `semantic_groups[]` — logical units (KPI card = number + label + icon)
- `reading_order[]` — visual reading sequence
- `quality_score` (0–10)

**See `references/pisa-schema-v2.1.md` for complete field definitions and examples.**

**Two strategies exist to fulfil this contract. Claude chooses the best one per situation.**

### Strategy 1 — XML Parsing (python-pptx)

The `extract_engine.py` (`services/extraction/`) reads the PPTX at the XML/data model level. Best when:
- Precise coordinate extraction is needed (e.g., for reproduction or retheme)
- The PPTX contains grouped shapes, rotated elements, or complex nesting
- Token-level colour extraction is required (exact hex values for theme mapping)
- Batch processing a large deck (faster than vision per slide)

**12-step pipeline:**

| Step | What | Output |
|------|------|--------|
| 1. Deep inventory | Flatten groups, compute oriented bounding boxes, flag decorative | Flat shape list |
| 2. Spatial analysis | Alignment axes, layout classification (DBSCAN clustering) | grid/columns/rows/stacked/radial/freeform |
| 3. Role assignment | Per-shape: title, subtitle, body, kpi_card, label, chart, table, image | Roles array |
| 4. Semantic groups | KPI units (number + label + icon), image + caption pairs | Group indices |
| 5. Intent classification | Heuristic scoring → LLM refinement if confidence < 0.65 | Intent + confidence |
| 6. Token extraction | KDTree colour matching, font token mapping | Design tokens |
| 7. Build template | Assemble V2.1 JSON with all fields | Template JSON |
| 8. Deduplication | LSH hash → weighted similarity (threshold 0.82) | Skip/replace/variant |
| 9. Register | Versioned library entry with source.origin="local" | Library update |
| 10. SVG preview | Render template → embed SVG string | Template with `svg` field |
| 11. Batch | Orchestrate steps 1–10 for all slides | Full deck extraction |
| 12. Report | Per-slide table: intent, confidence, quality, status | User-facing summary |

**Key rules:**
- Never auto-approve with confidence < 0.65 or ambiguous flag
- Maximum 8 content components per template (decorative excluded)
- Quality score < 4.0 = "draft" status, not used for generation without override

### Strategy 2 — Vision Analysis (Claude's native vision)

Claude looks at the slide image and produces the same V2.1 template JSON directly.
Best when:
- The slide is available as an image (screenshot, PDF page, photo of projected slide)
- The PPTX is not available (user has a photo or PDF, not the source file)
- Complex visual elements (infographics, custom illustrations) that XML parsing misses
- Quick analysis where approximate positions are sufficient
- The user asks to "look at this slide" rather than "parse this PPTX"

**Two-pass extraction for complex slides:**
1. **Pass 1 — Zone detection:** Identify distinct content zones. If a slide has a left panel with a bold statement and a right grid with KPIs, that's two zones with different intents.
2. **Pass 2 — Per-zone extraction:** Extract components within each zone, assigning the zone's intent.

**Vision extraction prompt (use this exact structure):**

```
Analyze this slide image. Produce a JSON object with these exact fields:
{
  "intent": "one of: cover, executive_summary, kpi_dashboard, comparison_columns,
    linear_process, timeline, matrix_2x2, single_insight, section_divider,
    conclusion_cta, data_table, chart_driven, agenda, thank_you,
    quote_testimonial, org_chart, before_after, swot, funnel,
    image_showcase, generic",
  "intent_confidence": 0.0-1.0,
  "secondary_intent": null or "intent if slide is compound (2+ intents fused)",
  "layout_type": "grid | columns | rows | stacked | radial | freeform | single",
  "layout_variant": "specific pattern e.g. grid_alternating_dark_light, columns_with_headers",
  "zones": [
    {"zone_id": "left_panel", "x_pct": 0, "y_pct": 0, "w_pct": 30, "h_pct": 100,
     "zone_intent": "single_insight", "component_indices": [0]}
  ],
  "components": [
    {
      "role": "title | subtitle | body | kpi_card | label | footer |
        chart | table | image | shape | decoration",
      "x_pct": 0-100, "y_pct": 0-100, "w_pct": 0-100, "h_pct": 0-100,
      "rotation": 0,
      "text_preview": "first 80 chars of visible text",

      "kpi": {
        "value": "23,2",
        "unit": "$B",
        "unit_position": "superscript | suffix | below",
        "label": "COMPLETION RATE",
        "sub_annotation": null,
        "trend": "up | down | stable | null"
      },

      "visual": {
        "bg_variant": "dark | light | accent | transparent",
        "border": "none | full | left | top",
        "has_separator": true,
        "has_icon": true,
        "icon_hint": "chart-line",
        "has_image_bg": false,
        "shape": "rectangle | rounded | circle"
      },

      "content_data": {
        "type": "timeline_entries | person_list | checklist | product_cards | key_value_list",
        "entries": [
          {"key": "Step 1", "text": "Define scope", "level": 0}
        ],
        "axis": "horizontal | vertical",
        "alternating": true
      }
    }
  ],
  "semantic_groups": [
    {"type": "kpi_unit | image_caption | standalone", "members": [0, 3]}
  ],
  "reading_order": [0, 1, 2, 3],
  "quality_score": 0-10,
  "source": {
    "origin": "local | registry | override",
    "file": "input.pptx or pack ID",
    "slide": 0,
    "extractor": "xml | vision | manual"
  }
}

Rules:
- Include kpi{} on EVERY kpi_card component — always separate value from unit from label
- Include visual{} on EVERY component — bg_variant and has_icon are the most important
- Use content_data{} when a body has internal structure (timelines, org charts, checklists)
- Use zones[] when the slide has 2+ distinct intent regions
- Ignore decorative elements (thin lines, tiny icons, background watermarks)
- Estimate positions as percentages (0 = left/top edge, 100 = right/bottom edge)
- icon_hint is a semantic description ("globe", "gear", "people"), not an asset path
- Score quality: +1 clear title, +1 clean layout, +1 structured KPI data, -0.5 per overlap
```

### Strategy Selection Logic

```
If user uploaded a .pptx file:
    → Prefer Strategy 1 (XML parsing) — precise, batch-capable
    → Fall back to Strategy 2 if parsing fails or returns low-quality results

If user uploaded an image, screenshot, or PDF:
    → Use Strategy 2 (vision) — the only option without PPTX source

If user asks "what kind of slide is this?" or "analyze this layout":
    → Use Strategy 2 (vision) — conversational, no need for precision

If both are available (PPTX + rendered image):
    → Use Strategy 1 for extraction, Strategy 2 for validation
    → Compare results: if they diverge significantly, flag for user review
```

**Both strategies produce the same V2 template JSON.** Everything downstream
(library registration, SVG preview, QA, generation, retheme) works identically
regardless of which strategy produced the template.

### A3. Present extraction report
Show per-slide table: slide#, intent, confidence, quality, layout, status.
Flag ⚠ slides. Ask user to confirm/override.

### A4. Offer export
"Export library as JSON for re-use in future sessions?"

---

## Workflow B — Generate

When user describes slides they want:

### B1. Parse brief into slide plan
For each slide: intent + key message + supporting content.
If persona is active, filter intents through preferred/discouraged lists.

### B1b. Resolve templates (local > remote)

For each slide in the plan, select the best template using this priority:

```
RESOLUTION ORDER (highest priority first):

1. LOCAL — templates extracted from the user's own deck this session
   source.origin = "local"
   These capture the user's actual brand, layout, and style.

2. OVERRIDE — registry templates the user has modified this session
   source.origin = "override"
   User said "I prefer this layout" or edited a registry template.

3. REGISTRY — templates installed from packs
   source.origin = "registry"
   Generic professional templates from the online catalog.
```

When multiple templates match an intent, prefer the one with:
1. Higher priority origin (local > override > registry)
2. Higher quality_score (within the same origin tier)
3. Better layout match for the content

The user can force a specific source:
- "Use my extracted KPI layout" → forces local
- "Use the registry version" → forces registry
- "Use the startup pack's cover" → forces a specific pack

If no templates exist for a required intent:
- If registry is available: auto-install the corporate essentials pack
- If offline: generate a minimal layout from the intent definition

### B2. Show SVG preview of selected templates
Before rendering the PPTX, show the user what each slide will look like
using the SVG renderer (via `show_widget`). This replaces the old text-only
confirmation block with a visual grid.

### B3. Render to PPTX
```javascript
const PptxGenJS = require('pptxgenjs');
let pptx = new PptxGenJS();
pptx.layout = 'LAYOUT_WIDE'; // 13.333" x 7.5"
// For each resolved template:
//   x_in = (x_pct / 100) * 13.333
//   y_in = (y_pct / 100) * 7.5
await pptx.writeFile({ fileName: 'output.pptx' });
```

### B4. Programmatic QA
Read the PPTX back with python-pptx and run ALL checks:
- **Token leaks**: scan all text for unresolved "token.*" strings
- **Overlaps**: compare shape bounding boxes, flag >5% area overlap
- **Out of bounds**: check shapes extend past slide edges
- **Empty shapes**: large shapes with no text content
- **Text overflow**: estimate text length vs shape capacity
- **Density**: word count and shape count vs persona/default limits
- **Theme compliance**: verify applied colours match theme JSON

If critical issues: fix and re-render. If warnings only: report and deliver.

### B5. Deliver
Provide PPTX as downloadable file.

---

## Workflow C — Retheme

1. Select source templates (by ID or intent)
2. Apply new theme via resolve_tokens()
3. Show SVG preview with new theme
4. Render and QA
5. Deliver

---

## Workflow D — Review / Score

Two review strategies, same 5-dimension rubric:

**Strategy 1 — Programmatic (from PPTX):** Parse the file with python-pptx and run
automated checks: density counting, title pattern detection, overlap detection, colour
compliance. Best for: density, title quality, and deck-level checks (duplicates, balance).
Can score ~60% of the rubric automatically.

**Strategy 2 — Vision (from image or SVG):** Claude looks at each slide and scores it
visually. Best for: clarity ("is the message obvious in 3 seconds?"), visual hierarchy
("is the eye drawn to the right element?"), and data presentation ("is this the right chart type?").
These are inherently visual judgments that programmatic checks cannot fully capture.

**Best practice: use both.** Programmatic checks catch objective violations (token leaks,
density, overlaps). Vision catches subjective quality issues (hierarchy, clarity, aesthetics).

### Score each slide on 5 dimensions (0–3 each):

| Dimension | Programmatic can measure | Vision better for |
|-----------|------------------------|-------------------|
| Clarity | — | ✅ Is the message obvious in 3 seconds? |
| Density | ✅ Word count, shape count, bullet count | — |
| Visual hierarchy | Partial (shape sizes, positions) | ✅ Is the eye drawn correctly? |
| Title quality | ✅ Label detection, length, punctuation | Insight vs label judgment |
| Data presentation | Partial (chart presence, labelling) | ✅ Right chart type? Good design? |

### Deck-level checks (always programmatic):
- Narrative arc: does the intent sequence follow the active persona's framework?
- Intent distribution: too many dividers? missing conclusion?
- Title uniqueness: no duplicates across deck

### Report
Structured report with per-slide scores + specific recommendations.
Target: ≥60% (e.g., 90+ out of 150 for a 10-slide deck).

---

## Workflow E — Library / Catalog

### Browse the Visual Catalog
```
User: "Show me all available templates"
User: "Show KPI dashboard layouts"
User: "What comparison layouts do I have?"
```
→ Filter library by intent/quality/layout → generate SVG grid → display via `show_widget`.
Each thumbnail shows the template's structure with the active theme applied.

### Multi-Theme Preview
```
User: "Show this template in light and dark themes"
User: "Compare corporate_dark vs corporate_light for the KPI dashboard"
```
→ Render same template with each theme → side-by-side SVG via `show_widget`.

### Import Templates
```
User: [uploads pisa_library.json]
User: "Load my PISA library"
```
→ Read JSON → restore all templates + SVGs into session library.
→ Report: "Loaded 47 templates across 18 intents. Library ready."

```
User: [uploads .pisa-collection ZIP]
```
→ Unpack → validate schema + checksums → merge templates → report.

### Install from Registry
```
User: "Install the finance pack"
```
→ web_fetch pack JSON from GitHub → merge into session library → confirm.
→ "Loaded Finance & Reporting: 14 templates, 8 intents, 2 themes."

### Export Library
```
User: "Export my library"
User: "Save the library for next time"
```
→ Generate pisa_library.json as downloadable artifact.
→ "Library exported: 52 templates, 4 themes. Upload this file to restore next session."

### Template Details
```
User: "Show me template corp_slide1_kpi"
User: "What's in the strategy consulting pack?"
```
→ Display single template SVG + full metadata (intent, quality, components, source).

---

## SVG Preview System

The SVG renderer produces structural previews directly from template JSON.
No external dependencies. Each role has distinctive visual treatment:

| Role | SVG Rendering |
|------|--------------|
| title | Filled bar with bold text + accent underline |
| subtitle | Lighter filled bar with medium text |
| body | White rect with accent left-border + simulated text lines |
| kpi_card | White card with accent top-border, large number, sparkline + trend arrow |
| chart | White rect with mini bar chart (7 bars, grid lines, axis) |
| table | Dark header row + alternating data rows + column dividers |
| image | Mountain silhouette + sun landscape placeholder |
| label | Small muted text, no background |
| footer | Thin separator line + small text |

Every slide SVG includes a top accent strip for brand identity.

---

## Programmatic QA Checks

These replace the former LibreOffice-based visual QA. All checks run by reading
the generated PPTX back with python-pptx:

| Check | Severity | What It Catches |
|-------|----------|----------------|
| token_leak | Critical | Unresolved "token.*" strings in text |
| overlap | Warning/Error | Content shapes overlapping >5% area |
| out_of_bounds | Error | Shapes extending past slide edges |
| empty_content | Warning | Large shapes with no text |
| text_overflow | Warning/Error | Text exceeding shape capacity |
| density_words | Warning/Error | Total words > persona limit |
| density_shapes | Warning | Content shapes > 8 |
| off_theme_color | Info | Colours not in the theme JSON |
| duplicate_title | Warning | Two slides with same title |
| narrative_arc | Info | Missing opening or closing slide |

**Critical/Error → fix before delivery. Warning → report. Info → note.**

---

## Density Limits (Always Enforce)

| Metric | Default Max | Persona can override |
|--------|-----------|---------------------|
| Words per slide body | 75 | Yes (25-90 depending on persona) |
| Bullet items per group | 5 | Yes (0 for keynote, 3 for executive) |
| Hierarchy levels | 2 | No |
| Content shapes | 6 | Yes (up to 8 for strategy) |

If exceeded during generation: flag, offer to split, NEVER silently ignore.

---

## 21 Canonical Intents (Compact)

cover · executive_summary · kpi_dashboard · comparison_columns · linear_process ·
timeline · matrix_2x2 · single_insight · section_divider · conclusion_cta ·
data_table · chart_driven · agenda · thank_you · quote_testimonial · org_chart ·
before_after · swot · funnel · image_showcase · generic

Each has defined shape/word limits — see pisa-slide-taxonomy.md for full specifications.

---

## Token Resolution

```python
def resolve_tokens(template, theme):
    import copy
    resolved = copy.deepcopy(template)
    FALLBACK = {"token.color.primary":"333333","token.font.heading":"Arial"}
    def walk(obj):
        if isinstance(obj, dict):
            for k, v in obj.items():
                if isinstance(v, str) and v.startswith("token."):
                    obj[k] = theme.get(v, FALLBACK.get(v, v))
                else: walk(v)
        elif isinstance(obj, list):
            for item in obj: walk(item)
    walk(resolved)
    return resolved
```

---

## Library Persistence (Tier 1)

The library resets between sessions. To persist:

**Export:** "Export my PISA library" → Claude generates pisa_library.json as downloadable artifact.
**Import:** User uploads pisa_library.json → Claude reads and restores all templates.
**Pack-based:** User installs packs from registry each session (fast — one web_fetch per pack).

The recommended flow for regular users:
1. First session: install packs from registry, extract from reference decks
2. End of session: export library
3. Next session: upload library OR re-install packs (both work)

---

## Separation of Concerns (Always Maintain)

Claude must NEVER hardcode visual properties in the renderer call. The visual outcome is
determined entirely by: template (structure) + theme (design) + content + persona (strategy).

If output doesn't look right:
- Wrong layout? → Select a different template
- Wrong colours? → Fix the theme JSON
- Too dense? → Reduce content, change persona, or split
- Bad structure? → Re-extract or manually adjust the template
- Wrong communication style? → Switch persona

---

## 12 Built-In Templates

Fallback set when no pack is installed. Claude generates minimal layouts from these definitions.
**Once a registry pack is installed, its templates replace the built-ins for matching intents.**

builtin_cover (8.0) · builtin_executive_summary (7.5) · builtin_kpi_dashboard (8.5) ·
builtin_comparison (7.5) · builtin_process (7.0) · builtin_timeline (7.0) ·
builtin_matrix (7.5) · builtin_insight (8.0) · builtin_section (9.0) ·
builtin_conclusion (7.0) · builtin_agenda (7.5) · builtin_thankyou (8.0)

These are the lowest priority tier. See **Resource Resolution** section for the full chain.

---

## Tier 2 Setup Reference

For users who want persistent local setup:

```bash
git clone <pisa-repo> && cd pisa
chmod +x scripts/bootstrap.sh && ./scripts/bootstrap.sh
```

7-step automated setup: directories, git, Python (python-pptx + scipy + sklearn),
Node (pptxgenjs), config, library seed, verification. No LibreOffice.
Under 2 minutes on modern hardware.

Tier 2 adds: persistent library, version tracking, diff reports, FastAPI backend (Phase 2),
.pisa package exchange, Office.js integration path (Phase 3).
