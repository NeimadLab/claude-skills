# PISA Canvas Schema V2.1

## What Changed from V2.0

| Feature | V2.0 | V2.1 |
|---------|------|------|
| KPI data | Flat `text_preview` string | Structured `kpi{}` with value, unit, label, annotation, trend |
| Visual treatment | None | `visual{}` per component: bg_variant, border, icon_hint, shape |
| Structured content | Everything is `text_preview` | `content_data{}` for timelines, org charts, checklists, product cards |
| Compound slides | Single `intent` forced | `secondary_intent` + `zones[]` for multi-intent slides |
| Schema version | 2 | 2.1 |

All new fields are **optional** — V2.0 canvases remain valid V2.1 canvases.

---

## Complete Component Schema

```json
{
  "role": "kpi_card",
  "x_pct": 25, "y_pct": 0, "w_pct": 25, "h_pct": 47,
  "rotation": 0,
  "word_count": 4,
  "text_preview": "[value] [unit] [label]

  // ── V2.1: Structured KPI data (when role = kpi_card) ──
  "kpi": {
    "value": "99.7",
    "unit": "%",
    "unit_position": "suffix",
    "label": "COMPLETION RATE",
    "sub_annotation": null,
    "trend": "up"
  },

  // ── V2.1: Visual treatment (any role) ──
  "visual": {
    "bg_variant": "dark",
    "border": "none",
    "border_color_token": null,
    "shape": "rectangle",
    "has_separator": true,
    "has_icon": true,
    "icon_hint": "chart-line",
    "has_image_bg": false,
    "image_bg_hint": null
  },

  // ── V2.1: Structured content (when role = body and content has internal structure) ──
  "content_data": {
    "type": "timeline_entries",
    "entries": [
      {"key": "Step 1", "text": "Define scope"},
      {"key": "Step 2", "text": "Execute plan"}
    ],
    "axis": "horizontal",
    "alternating": true
  }
}
```

### `kpi{}` — Structured KPI Data

Use when `role` = `kpi_card`. Replaces guessing from `text_preview`.

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `value` | string | Yes | The display number: "12.4", "N°3", "+1200", "75%" |
| `unit` | string | No | Unit separate from value: "$B", "$M", "%", "km/h" |
| `unit_position` | enum | No | `superscript` \| `suffix` \| `below` — how unit relates to value |
| `label` | string | Yes | The descriptor: "TOTAL USERS", "SCORE" |
| `sub_annotation` | string | No | Footnote or context: "*As of Dec 2025", "Rounded" |
| `trend` | enum | No | `up` \| `down` \| `stable` \| `null` |

### `visual{}` — Component Visual Treatment

Use on any component. Captures how the component looks beyond its position.

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `bg_variant` | enum | No | `dark` \| `light` \| `accent` \| `accent2` \| `transparent` |
| `border` | enum | No | `none` \| `full` \| `left` \| `top` \| `bottom` |
| `border_color_token` | string | No | Token reference for border colour |
| `shape` | enum | No | `rectangle` \| `rounded` \| `circle` \| `pill` |
| `has_separator` | bool | No | Horizontal line between number and label |
| `has_icon` | bool | No | Component includes an icon/illustration |
| `icon_hint` | string | No | Semantic description: "globe", "chart-line", "people" |
| `has_image_bg` | bool | No | Component has a background image |
| `image_bg_hint` | string | No | Description: "abstract gradient", "gradient blue-purple" |

### `content_data{}` — Structured Body Content

Use when `role` = `body` but the content has internal structure that shouldn't be flattened.

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `type` | enum | Yes | `timeline_entries` \| `person_list` \| `checklist` \| `product_cards` \| `key_value_list` |
| `entries[]` | array | Yes | Each entry has `key`, `text`, and optional `emphasis[]` |
| `axis` | enum | No | `horizontal` \| `vertical` (for timelines) |
| `alternating` | bool | No | Entries alternate position (above/below for timelines) |
| `hierarchy` | bool | No | Entries have parent/child relationships (for org charts) |

**Entry schema:**
```json
{"key": "Phase 1", "text": "Initial rollout", "level": 0}
```

---

## Complete Canvas Schema V2.1

```json
{
  "schema_version": 2.1,
  "id": "prim_example_a8f2c1d9",
  "intent": "kpi_dashboard",
  "intent_confidence": 0.92,
  
  // ── V2.1: Compound intent support ──
  "secondary_intent": null,
  "secondary_confidence": null,
  "zones": [],
  
  "layout_type": "grid",
  "layout_variant": "grid_alternating_dark_light",
  
  "semantic_groups": [
    {"type": "kpi_unit", "members": [1, 4]},
    {"type": "kpi_unit", "members": [2, 5]}
  ],
  
  "components": [],
  "reading_order": [0, 1, 2, 3, 4, 5, 6, 7, 8],
  
  "design_tokens": {
    "colors": {"#1E3A5F": "token.color.primary"},
    "fonts": {"Calibri": "token.font.heading"},
    "unmapped": []
  },
  
  "density": {
    "content_shapes": 8,
    "total_words": 42,
    "decorative_removed": 3
  },
  
  "quality_score": 8.5,
  "status": "approved",
  "version": 1,
  
  "source": {
    "origin": "local",
    "file": "input.pptx",
    "slide": 1,
    "extracted_at": "2026-03-21T18:00:00",
    "extractor": "vision",
    "strategy": "vision_v1"
  },
  
  "_content_hash": "a8f2c1d9"
}
```

### `zones[]` — For Compound Slides

When a slide has two or more distinct intent regions:

```json
"zones": [
  {
    "zone_id": "left_panel",
    "x_pct": 0, "y_pct": 0, "w_pct": 30, "h_pct": 100,
    "zone_intent": "single_insight",
    "component_indices": [0, 1]
  },
  {
    "zone_id": "right_top",
    "x_pct": 30, "y_pct": 0, "w_pct": 70, "h_pct": 50,
    "zone_intent": "timeline",
    "component_indices": [2, 3, 4, 5]
  }
]
```

### `layout_variant` — Specific Layout Patterns

Extends `layout_type` with the specific visual pattern observed:

| layout_type | layout_variant examples |
|-------------|----------------------|
| grid | `grid_uniform`, `grid_alternating_dark_light`, `grid_2x4`, `grid_3x2` |
| columns | `columns_equal`, `columns_hero_left`, `columns_with_headers` |
| rows | `rows_timeline_alternating`, `rows_stacked_cards` |
| radial | `radial_hub_spoke`, `radial_circular` |
| freeform | `freeform_scattered`, `freeform_organic` |

---

