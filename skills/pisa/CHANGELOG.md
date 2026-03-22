# PISA Changelog

## [1.0.0] — 2026-03-21

### Added
- Schema V2.1: `kpi{}`, `visual{}`, `content_data{}`, compound intents, `layout_variant`
- 8 communication personas: strategy, executive, keynote, startup, technical, sales, workshop, academic
- 61 primitives across 4 packs: Corporate Essentials (24), Finance & Reporting (14), Strategy Consulting (12), Startup Pitch (11)
- 3 themes: Corporate Dark, Corporate Light, Finance Dark
- SVG renderer V2.1: dark/light card rendering, structured KPI display, trend arrows
- Programmatic QA engine: 10 checks + V2.1 field validation
- Dual extraction strategy: XML parsing (python-pptx) + Vision (Claude native)
- Online registry: install packs, themes, personas with one command
- 9 documentation pages (GitHub-rendered markdown)
- Bootstrap script for local development (Tier 2)
- Zero external dependencies (no LibreOffice, no Pillow)
