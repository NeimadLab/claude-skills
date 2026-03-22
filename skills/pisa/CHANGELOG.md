# PISA Changelog

## [1.2.0] — 2026-03-22

### Added — 4-Layer Architecture
- **Canvas × Style = Template** model documented as the core structuring concept
- 4-layer model: Canvas (skeleton) → Style (personality) → Template (browsable artifact) → Theme/Persona/Content (render time)
- This model is now the first section in SKILL.md, README, architecture docs, getting-started

### Added — Style System
- 5 built-in styles: bold, minimal, gradient, split, photo
- Style JSONs in `registry/styles/` with visual personality rules
- Styles registered in `registry.json` alongside packs/themes/personas
- Style commands in SKILL.md: "use bold style", "show all styles", per-slide overrides

### Changed
- **Renamed "canvas" → "template"** in all user-facing artifacts (packs, registry, gallery, docs)
- Canvas is now an internal authoring concept — users see and interact with templates
- `canvas_to_svg.py` → `template_to_svg.py`, `qa_canvas()` → `qa_template()`
- JSON key: `"canvases"` → `"templates"` in all packs and registry
- Merged `subskills/` into `services/extraction/` — flat service architecture
- 12-step extraction pipeline documented in main SKILL.md (was in deleted sub-SKILL.md)

## [1.1.1] — 2026-03-22

### Changed
- Renamed "primitive" → "canvas" across codebase (intermediate step, now "template")
- Unified resource resolution rules
- Source tracking on all resources
- Complete persona specs: all 8 have `max_content_shapes`

### Added
- Roadmap items: theme transformation depth, persona shaping, typed placeholders

## [1.1.0] — 2026-03-22

### Added
- PPTX generator (`services/generator/generate.js`) — template + theme + content → PPTX
- Built-in registry URL in SKILL.md frontmatter — users don't need to configure anything
- Template resolution order: local > override > registry
- `source.origin` field on all templates

### Improved
- All 61 templates enriched across 4 packs:
  - bg_variant distribution: 100% light → 55% light / 34% dark / 11% accent
  - Icons: 0 → 61 components with icon_hint
  - KPI labels: 0 → 31 KPI cards with structured labels, annotations, trends
  - Layout variants: 1 (uniform) → 15 unique patterns

## [1.0.0] — 2026-03-21

### Added
- Schema V2.1: `kpi{}`, `visual{}`, `content_data{}`, compound intents, `layout_variant`
- 8 communication personas
- 61 templates across 4 packs
- 3 themes, SVG renderer, programmatic QA engine
- Online registry, 9 documentation pages, zero external dependencies
