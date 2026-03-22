# PISA Changelog

## [1.1.0] — 2026-03-22

### Added
- PPTX generator (`services/generator/generate.js`) — primitive + theme + content → PPTX
- Built-in registry URL in SKILL.md frontmatter — users don't need to configure anything
- Primitive resolution order: local > override > registry
- `source.origin` field on all primitives

### Improved
- All 61 primitives enriched across 4 packs:
  - bg_variant distribution: 100% light → 55% light / 34% dark / 11% accent
  - Icons: 0 → 61 components with icon_hint
  - KPI labels: 0 → 31 KPI cards with structured labels, annotations, trends
  - Layout variants: 1 (uniform) → 15 unique patterns

## [1.0.0] — 2026-03-21

### Added
- Schema V2.1: `kpi{}`, `visual{}`, `content_data{}`, compound intents, `layout_variant`
- 8 communication personas
- 61 primitives across 4 packs
- 3 themes, SVG renderer, programmatic QA engine
- Online registry, 9 documentation pages, zero external dependencies
