# Slide Taxonomy — 21 Canonical Intents

Every slide maps to one of 21 intents. This classification drives template selection, density enforcement, and layout expectations.

| # | Intent | Purpose | Typical Components |
|---|--------|---------|-------------------|
| 1 | `cover` | Opening slide | Title, subtitle, date, branding |
| 2 | `executive_summary` | Key findings up front | Title, 3-5 insight bullets, KPI highlights |
| 3 | `kpi_dashboard` | Numeric overview | 4-8 KPI cards with values, units, labels |
| 4 | `comparison_columns` | Side-by-side analysis | 2-4 columns with headers and body |
| 5 | `linear_process` | Step-by-step flow | Numbered stages with arrows |
| 6 | `timeline` | Chronological events | Milestones on a time axis |
| 7 | `matrix_2x2` | Four-quadrant analysis | 2×2 grid with axis labels |
| 8 | `single_insight` | One bold statement | Large text, minimal decoration |
| 9 | `section_divider` | Chapter separator | Section title, background image |
| 10 | `conclusion_cta` | Closing with action | Summary, next steps, call to action |
| 11 | `data_table` | Structured data | Table with header row, data rows |
| 12 | `chart_driven` | Chart as hero element | Bar/line/pie chart with annotation |
| 13 | `agenda` | Session/meeting outline | Numbered topics with timing |
| 14 | `thank_you` | Closing slide | Thank you, contact info |
| 15 | `quote_testimonial` | External voice | Quote text, attribution, photo |
| 16 | `org_chart` | Hierarchy | Person cards with connections |
| 17 | `before_after` | Transformation | Two-state comparison |
| 18 | `swot` | Strategic analysis | 2×2 with S/W/O/T labels |
| 19 | `funnel` | Stage conversion | Narrowing stages with metrics |
| 20 | `image_showcase` | Visual-first slide | Full-bleed or hero image |
| 21 | `generic` | Fallback | Anything that doesn't fit above |

## Intent Detection

During extraction, PISA assigns an intent based on:
- Component count and roles (many KPI cards → `kpi_dashboard`)
- Layout pattern (2×2 grid → `matrix_2x2`)
- Text patterns (numbered steps → `linear_process`)
- Position patterns (single centered text → `single_insight`)

Confidence scores range 0–1. Below 0.7, the intent is flagged for user review.

## Compound Intents

Some slides span two intents. V2.1 supports `secondary_intent` and `zones[]` for these cases. Example: a slide that is 30% `single_insight` (left panel) and 70% `kpi_dashboard` (right grid).
