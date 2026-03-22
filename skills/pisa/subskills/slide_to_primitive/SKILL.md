# PISA Sub-Skill — Slide to Primitive Extractor (V2)

## Trigger

Use this sub-skill when:
- User provides a PPTX and asks to "extract primitives", "learn from slides", "add to library", or "reverse engineer"
- User wants to feed existing slides into the PISA reusable library
- User provides a reference deck and wants PISA to replicate its patterns

## Role in PISA Architecture

This is **Strategy 1 (XML Parsing)** for fulfilling the extraction contract.
It reads PPTX at the data model level for precise coordinate and colour extraction.
**Strategy 2 (Vision)** uses Claude's native image understanding for the same contract.
Both produce identical V2 primitive JSON. See main SKILL.md for strategy selection logic.

Use this strategy when: PPTX source file is available, precise positions needed, batch processing,
token-level colour extraction required.
Use vision instead when: only image/screenshot/PDF available, quick analysis, visual-heavy slides.

## What V2 Handles

Real-world slides: grouped shapes (recursive flattening), rotated elements (oriented bounding boxes), freeform scatter layouts (DBSCAN band clustering), decorative elements mixed with content (automatic filtering), KPI cards composed of separate shapes (semantic group detection).

## Dependencies

- python-pptx, numpy, scipy (KDTree), scikit-learn (DBSCAN)
- services/svg/primitive_to_svg.py for SVG previews (pure Python, no external deps)
- No LibreOffice. No Pillow. No subprocess calls.

## 12-Step Pipeline

| Step | Name | Output |
|------|------|--------|
| 1 | Deep Inventory | Flat shape list with absolute coords, oriented bounding boxes, decorative flags |
| 2 | Spatial Analysis | Alignment axes, layout classification (grid/columns/rows/stacked/radial/freeform), DBSCAN reading order |
| 3 | Role Assignment | Per-shape: title, subtitle, body, kpi_card, label, footer, image, chart, table, shape, decoration |
| 4 | Semantic Groups | KPI units (number + label + icon), image + caption pairs |
| 5 | Intent Classification | Two-pass: heuristic scoring → LLM refinement if confidence < 0.65 or ambiguous |
| 6 | Token Extraction | KDTree-accelerated colour matching, font token mapping |
| 7 | Build Primitive | V2 JSON with layout_type, semantic_groups, reading_order, quality_score, content_hash, version |
| 8 | Deduplication | LSH position-hash pre-filter → weighted role-aware similarity (threshold: 0.82) |
| 9 | Register | Versioned library: same-source = increment version, near-duplicate = skip/replace/variant |
| 10 | SVG Preview | Pure-Python SVG generation from primitive + theme. Embedded in primitive JSON as `svg` field. |
| 11 | Batch | Full-deck orchestration for all slides |
| 12 | Report | Per-slide summary with intent, confidence, quality, registration status |

## Key Rules
- Never auto-approve with confidence < 0.65 OR ambiguous flag
- Never register with unmapped tokens without user confirmation
- Maximum 8 content components per primitive (decorative excluded)
- Maximum 75 words per body component (overridden by persona)
- Quality score < 4.0 = "draft" status, not used for generation without override
- Source attribution is immutable across versions
