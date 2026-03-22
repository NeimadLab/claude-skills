# Quality System & Programmatic QA

## Density Limits

Every slide is checked against density limits. Personas override the defaults.

| Metric | Default | Executive | Keynote | Strategy |
|--------|:-------:|:---------:|:-------:|:--------:|
| Words per body | 75 | 60 | 25 | 90 |
| Bullets per group | 5 | 3 | 0 | 5 |
| Hierarchy levels | 2 | 2 | 1 | 2 |
| Content shapes | 6 | 5 | 3 | 7 |

If exceeded during generation: flag, offer to split. Never silently ignore.

## 10 Programmatic QA Checks

These run by reading the generated PPTX back with python-pptx. No LibreOffice needed.

| Check | Severity | What It Catches |
|-------|:--------:|-----------------|
| `token_leak` | 🔴 Critical | Unresolved "token.*" strings in text |
| `overlap` | 🟡 Warning | Content shapes overlapping >5% area |
| `out_of_bounds` | 🔴 Error | Shapes extending past slide edges |
| `empty_content` | 🟡 Warning | Large shapes with no text |
| `text_overflow` | 🟡 Warning | Text exceeding shape capacity |
| `density_words` | 🟡 Warning | Total words > persona limit |
| `density_shapes` | 🟡 Warning | Content shapes > persona limit |
| `off_theme_color` | ⚪ Info | Colors not in the theme JSON |
| `duplicate_title` | 🟡 Warning | Two slides with same title |
| `narrative_arc` | ⚪ Info | Missing opening or closing slide |

**V2.1 additional checks** (on primitive JSON before rendering):
- KPI cards missing `kpi{}` → warning
- Components missing `visual{}` → info
- Structured body without `content_data{}` → info
- Compound slides without `zones[]` → warning

**Critical/Error → fix before delivery. Warning → report. Info → note.**

## Title Quality Rules

1. Insight, not label ("Revenue grew 23% in Q3" not "Q3 Revenue")
2. Under 12 words
3. No ending punctuation
4. Active voice
5. Unique across the deck

## Primitive Quality Scores

- **≥ 8.0** → Approved — ready for production use
- **4.0–7.9** → Candidate — usable but may need refinement
- **< 4.0** → Draft — needs significant work

## Review Rubric (5 Dimensions)

Each slide scores 0–3 on five dimensions (max 15 per slide):

1. **Clarity** — is the main message immediately obvious?
2. **Visual hierarchy** — do the eyes follow the right path?
3. **Data presentation** — are numbers, charts, comparisons effective?
4. **Consistency** — does it match the theme and other slides?
5. **Narrative** — does it advance the deck's story?

Target: ≥ 60% of maximum across the deck.
