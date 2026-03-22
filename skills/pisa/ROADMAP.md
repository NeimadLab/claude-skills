# PISA Roadmap

> Last updated: March 22, 2026

## Current state: v1.1

The pipeline works end-to-end: canvases → theme resolution → PPTX generation → QA. 61 canvases across 4 packs, enriched with dark/light alternation, icons, KPI labels, and trend indicators. The registry is live, the generator produces real PPTX files.

**The honest gap:** slides are structurally correct but visually basic. A McKinsey or TED deck has craft — spacing, shadows, gradient fills, connected process arrows, micro-interactions. Closing that gap is the focus of everything below.

---

## ✅ Done

### v1.0 — Foundation (March 21)
- [x] Schema V2.1: `kpi{}`, `visual{}`, `content_data{}`, compound intents
- [x] 61 canvases across 4 packs (Corporate, Finance, Strategy, Startup)
- [x] 8 personas, 3 themes, 21 intent taxonomy
- [x] SVG renderer, programmatic QA engine (10 checks)
- [x] XML extraction engine (python-pptx) + vision extraction (Claude native)
- [x] GitHub registry: install packs with one command
- [x] 9 documentation pages, bootstrap script, CI validation

### v1.1 — Generator + Enrichment (March 22)
- [x] PPTX generator (`generate.js`): canvas + theme + content → real PPTX
- [x] All 61 canvases enriched: dark/light/accent cards, 61 icons, 31 KPI labels
- [x] 15 layout variants (was 1)
- [x] Built-in registry URL — zero user configuration
- [x] Canvas resolution order: local > override > registry
- [x] `source.origin` field on all canvases

---

## 🔨 v1.2 — Make It Beautiful
**Goal:** Generated slides that look designed, not computed.
**Target:** April 2026

### Spacing & polish
- [ ] Consistent internal margins (card padding = 0.15", not touching edges)
- [ ] Breathing room between cards (gap = 2% of slide width minimum)
- [ ] Title-to-content spacing rule (12% gap after title area)
- [ ] Footer zone reserved (bottom 5% never used by content)

### Visual depth
- [ ] Subtle gradient fills on dark cards (5% lighter at bottom)
- [ ] Drop shadows on KPI cards (2px, 10% opacity)
- [ ] Rounded corners everywhere (rectRadius 0.08-0.12")
- [ ] Accent bar thickness consistency (3px top, 2px left)

### Text hierarchy
- [ ] Title: 28pt bold, primary color, always left-aligned on content slides
- [ ] KPI value: 36-44pt bold, high contrast, centered in card
- [ ] KPI unit (superscript): 40% of value size, accent color
- [ ] KPI label: 9pt uppercase, letter-spacing 1.5, muted color
- [ ] Body text: 12pt, 1.3x line height, left-aligned with 5pt paragraph spacing
- [ ] Smart font sizing: auto-shrink when text overflows (min 9pt)

### New themes
- [ ] `modern_minimal` — white bg, thin 1px borders, generous whitespace, no accent bars
- [ ] `bold_gradient` — dark bg with gradient accent overlays, high contrast numbers
- [ ] `warm_corporate` — cream bg, navy text, gold accents (consulting style)
- [ ] Theme preview: same KPI dashboard rendered in all themes side-by-side

### Hero canvases (top 10 redesign)
- [ ] Cover: full-bleed color block left + title right, or centered with gradient background
- [ ] KPI dashboard: card grid with micro-sparklines, trend badges, proper unit placement
- [ ] Executive summary: insight columns with header badges and numbered key points
- [ ] Process flow: steps connected with arrows/lines, numbered circle badges
- [ ] Comparison: visual weight on recommended option (thicker border, accent bg)
- [ ] Timeline: horizontal axis with milestone markers, alternating above/below
- [ ] Chart+insight: chart occupying 60% with annotation panel
- [ ] Section divider: full-bleed with semi-transparent text overlay
- [ ] SWOT: colored quadrants (green/red/blue/yellow) with corner labels
- [ ] Conclusion/CTA: numbered actions with checkbox icons

### Theme transformation depth
Right now themes swap colors. They should transform the canvas feel:
- [ ] Theme controls spacing: `modern_minimal` = generous padding, `bold_gradient` = tight
- [ ] Theme controls corner radius: 0 for minimal, 0.12" for rounded
- [ ] Theme controls shadow: none for minimal, soft for corporate, sharp for bold
- [ ] Theme controls accent bar style: none / top-only / left-only / dual
- [ ] Same canvas + different theme = visually distinct result (not just recolored)

### Persona shaping beyond density
Personas should transform canvas selection and content, not just cap word counts:
- [ ] Persona influences component visibility: `keynote` hides body text, enlarges title
- [ ] Persona influences title generation: `strategy` → insight sentence, `keynote` → bold claim
- [ ] Persona influences which canvases are eligible: `executive` never selects `funnel` or `org_chart`
- [ ] Persona influences slide count: auto-split when content exceeds persona density

---

## 📊 v1.3 — Real Data
**Goal:** Charts and tables with actual data, not placeholders.
**Target:** May 2026

### Chart rendering
- [ ] Bar charts (vertical, horizontal, stacked, grouped) from JSON data
- [ ] Line charts with axes, labels, data points, gridlines
- [ ] Pie/donut charts with segment labels
- [ ] Waterfall/bridge charts (finance use case)
- [ ] Chart colors mapped to theme tokens automatically
- [ ] Source line below every chart

### Table rendering
- [ ] User data → formatted PPTX table
- [ ] Header row: theme primary bg, bold white text
- [ ] Alternating row shading (surface/bg alternation)
- [ ] Right-aligned numbers, left-aligned text, centered headers
- [ ] Conditional highlighting (green/red for positive/negative variance)

### Data input
- [ ] Inline JSON data in content override
- [ ] CSV upload → auto-detect chart type
- [ ] Reference uploaded Excel → extract sheet data

### Typed placeholders
Canvases should have typed slots, not just `text_preview` strings:
- [ ] `{{kpi_value}}`, `{{kpi_label}}`, `{{kpi_unit}}` — generator knows exactly where KPI data goes
- [ ] `{{chart_data}}` — accepts JSON data array, renders the right chart type
- [ ] `{{table_data}}` — accepts rows/columns, formats automatically
- [ ] `{{logo}}` — placement zone that accepts an image upload
- [ ] `{{date}}`, `{{author}}`, `{{slide_number}}` — auto-filled metadata
- [ ] Unfilled placeholders render as labeled gray boxes (not blank space)

---

## 🔬 v1.4 — Extract & Learn
**Goal:** Upload any deck → extract canvases that are actually reusable.
**Target:** June 2026

### Extraction quality
- [ ] Test on 20+ real-world decks (diverse industries and styles)
- [ ] Handle grouped shapes, rotated elements, nested tables
- [ ] Extract real chart data from embedded Excel objects
- [ ] Color mapping: exact hex → nearest theme token
- [ ] Font mapping: detected fonts → theme font tokens
- [ ] Brand auto-detection: logo, primary palette, fonts from any uploaded deck

### Extract → reuse pipeline
- [ ] Upload deck A → extract → generate new content in deck A's style
- [ ] "Clone this slide's layout with my data" — one-shot reuse
- [ ] Confidence calibration: when to trust extraction vs flag for review

---

## 🌍 v1.5 — Community & Ecosystem
**Goal:** Other people contribute canvases, packs, and themes.
**Target:** July 2026

### Contribution system
- [ ] CI validates submitted canvases (schema compliance + SVG preview)
- [ ] PR template for new packs with quality checklist
- [ ] Pack review rubric (visual quality, intent coverage, theme support)

### GitHub Pages catalog
- [ ] Browse all packs with SVG previews
- [ ] Pack detail page: intent coverage, theme previews
- [ ] Search/filter by intent, theme, persona
- [ ] Theme preview tool: upload JSON → see all 21 intents

### Ecosystem growth
- [ ] Theme builder guide (brand guide → theme JSON)
- [ ] Custom persona builder
- [ ] Industry-specific packs: healthcare, legal, real estate, education
- [ ] Industry-specific personas

---

## 🧠 v2.0 — Intelligence
**Goal:** PISA doesn't just render — it advises.
**Target:** Q4 2026

### Slide advisor
- [ ] "Too much text" → auto-suggest split
- [ ] "No context on KPIs" → suggest annotations
- [ ] "Slides 4 and 7 repeat" → flag redundancy
- [ ] Narrative arc check: does the deck tell a coherent story?

### Auto-layout
- [ ] Content → auto-select best canvas (no user choice needed)
- [ ] "Reflow this slide" → show 3 alternative layouts as SVG
- [ ] Content-aware: long text → stacked, many numbers → grid

### Brand intelligence
- [ ] Upload brand guidelines PDF → auto-generate theme + canvases
- [ ] "Does this deck match our brand?" → compliance score

---

## Backlog (unscheduled)

**Quality of life:** batch operations, undo/redo, Google Slides export, PDF export without LibreOffice

**Advanced rendering:** entrance animations, speaker notes generation, handout mode (2-up/4-up), accessibility (alt text, reading order, contrast)

**Integration:** Claude MCP server (PISA as a callable tool), VS Code extension, Figma import/export, Notion page → deck

---

## Contributing

Pick any unchecked item, open an issue, submit a PR. The [CONTRIBUTING.md](CONTRIBUTING.md) has the standards.

The highest-impact work right now is in **v1.2** — making slides beautiful. If you can design a better version of any canvas, that's the most valuable contribution.
