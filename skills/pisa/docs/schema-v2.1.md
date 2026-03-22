# Schema V2.1 — Template JSON Format

## Overview

A **template** is the combination of a canvas (structure) and a style (visual personality). It's the concrete JSON artifact that lives in packs, appears in the gallery, and gets selected during generation.

The JSON format is the same whether you're looking at a raw canvas or a fully styled template — the difference is that templates have `visual{}` properties populated by the style rules (bg_variant, icons, borders, etc.), while raw canvases leave those at defaults.

V2.1 added three component-level extensions that improved reproduction fidelity from 50% to 85% in testing:

- **`kpi{}`** — structured KPI data (value, unit, label, annotation, trend)
- **`visual{}`** — component visual treatment (bg_variant, icons, borders)
- **`content_data{}`** — structured body content (timelines, org charts, checklists)
- **`zones[]`** — compound slides with multiple intents

All new fields are optional. V2.0 templates remain valid V2.1 templates.

## Complete Template Structure

```json
{
  "schema_version": 2.1,
  "id": "prim_example_a8f2c1d9",
  "intent": "kpi_dashboard",
  "intent_confidence": 0.92,
  "secondary_intent": null,
  "layout_type": "grid",
  "layout_variant": "grid_alternating_dark_light",
  "zones": [],
  "components": [ ... ],
  "semantic_groups": [ ... ],
  "reading_order": [0, 1, 2, 3],
  "quality_score": 8.5,
  "source": {
    "origin": "local | registry | override",
    "file": "input.pptx",
    "slide": 1,
    "extractor": "xml | vision | manual"
  }
}
```

### Template Resolution Order

When generating slides, Claude selects templates using this priority:

1. **`local`** — extracted from the user's own deck this session. Always preferred.
2. **`override`** — registry templates the user has modified. Second priority.
3. **`registry`** — installed from packs. Fallback.

Within the same origin tier, higher `quality_score` wins.

## kpi{} — Structured KPI Data

Use on every component with `role: "kpi_card"`.

```json
{
  "role": "kpi_card",
  "x_pct": 25, "y_pct": 0, "w_pct": 25, "h_pct": 47,
  "kpi": {
    "value": "12.4",
    "unit": "$B",
    "unit_position": "superscript",
    "label": "COMPLETION RATE",
    "sub_annotation": "null",
    "trend": "up"
  }
}
```

| Field | Type | Description |
|-------|------|-------------|
| `value` | string | The display number: "12.4", "N°3", "+1200" |
| `unit` | string | Unit separate from value: "$B", "%", "km/h" |
| `unit_position` | enum | `superscript` \| `suffix` \| `below` |
| `label` | string | Descriptor: "COMPLETION RATE" |
| `sub_annotation` | string | Context: "null", "Rounded" |
| `trend` | enum | `up` \| `down` \| `stable` \| `null` |

## visual{} — Component Visual Treatment

Use on any component.

```json
{
  "visual": {
    "bg_variant": "dark",
    "border": "left",
    "has_separator": true,
    "has_icon": true,
    "icon_hint": "chart-line",
    "has_image_bg": false,
    "shape": "rectangle"
  }
}
```

| Field | Type | Description |
|-------|------|-------------|
| `bg_variant` | enum | `dark` \| `light` \| `accent` \| `transparent` |
| `border` | enum | `none` \| `full` \| `left` \| `top` \| `bottom` |
| `has_separator` | bool | Line between number and label |
| `has_icon` | bool | Component includes an icon |
| `icon_hint` | string | Semantic description: "globe", "gear" |
| `shape` | enum | `rectangle` \| `rounded` \| `circle` \| `pill` |

## content_data{} — Structured Body Content

Use when `role: "body"` has internal structure that shouldn't flatten to text.

```json
{
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

Types: `timeline_entries`, `person_list`, `checklist`, `product_cards`, `key_value_list`

## zones[] — Compound Slides

When a slide fuses multiple intents:

```json
{
  "intent": "timeline",
  "secondary_intent": "kpi_dashboard",
  "zones": [
    {"zone_id": "left", "x_pct": 0, "y_pct": 0, "w_pct": 30, "h_pct": 100,
     "zone_intent": "single_insight", "component_indices": [0]},
    {"zone_id": "right", "x_pct": 30, "y_pct": 0, "w_pct": 70, "h_pct": 100,
     "zone_intent": "timeline", "component_indices": [1, 2, 3]}
  ]
}
```

## layout_variant

Extends `layout_type` with the specific visual pattern:

| layout_type | layout_variant examples |
|-------------|------------------------|
| grid | `grid_uniform`, `grid_alternating_dark_light`, `grid_2x4` |
| columns | `columns_equal`, `columns_hero_left`, `columns_with_headers` |
| rows | `rows_timeline_alternating`, `rows_stacked_cards` |
| radial | `radial_hub_spoke` |

## Component Roles

`title`, `subtitle`, `body`, `kpi_card`, `chart`, `table`, `image`, `label`, `footer`, `shape`, `decoration`
