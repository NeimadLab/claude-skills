# PISA Changelog

## [1.1.1] — 2026-03-22

### Changed
- **Renamed "primitive" → "canvas"** across entire codebase (303 occurrences, 37 files)
  - `slide_to_primitive/` → `slide_to_canvas/`
  - `primitive_to_svg.py` → `canvas_to_svg.py`
  - `qa_primitive()` → `qa_canvas()`
  - JSON key: `"primitives"` → `"canvases"` in all packs and registry
- Unified resource resolution rules: one section for all resource types (canvases, personas, themes)
- Source tracking on all resources: personas get `version` + `source.origin`, themes get `_version` + `_source`
- Complete persona specs: all 8 have `max_content_shapes`

### Added
- Roadmap items: theme transformation depth, persona shaping, typed placeholders

## [1.1.0] — 2026-03-22

### Added
- PPTX generator (`services/generator/generate.js`) — canvas + theme + content → PPTX
- Built-in registry URL in SKILL.md frontmatter — users don't need to configure anything
- Canvas resolution order: local > override > registry
- `source.origin` field on all canvases

### Improved
- All 61 canvases enriched across 4 packs:
  - bg_variant distribution: 100% light → 55% light / 34% dark / 11% accent
  - Icons: 0 → 61 components with icon_hint
  - KPI labels: 0 → 31 KPI cards with structured labels, annotations, trends
  - Layout variants: 1 (uniform) → 15 unique patterns

## [1.0.0] — 2026-03-21

### Added
- Schema V2.1: `kpi{}`, `visual{}`, `content_data{}`, compound intents, `layout_variant`
- 8 communication personas
- 61 canvases across 4 packs
- 3 themes, SVG renderer, programmatic QA engine
- Online registry, 9 documentation pages, zero external dependencies
