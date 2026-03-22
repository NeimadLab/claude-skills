# PISA Persona System

## What a Persona Is

A persona is a **generation strategy** that controls how PISA builds a deck. It affects:
- Which primitives are preferred or forbidden
- What density limits apply (overriding defaults)
- How titles are written (insight vs question vs action vs label)
- How content is distributed across slides (thin vs dense)
- What narrative framework governs slide sequencing
- Whether bullets are acceptable
- What visual ratio (data vs text vs image) is expected
- Typography scale (compact vs large vs dramatic)

A persona is NOT a theme. Themes control colours/fonts. Personas control communication strategy.
You combine a persona + a theme + a pack: "Generate a Q3 review using **strategy** persona,
**finance** pack, **corporate_dark** theme."

---

## Persona JSON Schema

```json
{
  "persona_id": "strategy",
  "name": "Strategy Consulting",
  "short_description": "McKinsey/BCG/Bain — data-rich, insight-led, Pyramid narrative",
  "archetype": "Management consulting deliverable for C-suite decision-making",
  "origin": "Derived from McKinsey, BCG, Bain public presentation standards",

  "narrative": {
    "framework": "pyramid",
    "description": "Main conclusion first, then supporting arguments grouped by MECE logic",
    "required_sections": ["cover", "executive_summary", "body", "conclusion"],
    "optional_sections": ["appendix", "methodology"],
    "opening_style": "Executive summary with 3-5 key findings",
    "closing_style": "Actionable recommendations with clear owners and timelines"
  },

  "density": {
    "max_words_body": 90,
    "max_bullets": 5,
    "max_hierarchy_levels": 2,
    "max_content_shapes": 7,
    "slide_density": "high",
    "min_data_slides_pct": 40
  },

  "titles": {
    "style": "assertive_insight",
    "description": "Every title is a complete sentence stating the slide's conclusion",
    "rules": [
      "Must be a full insight sentence, not a topic label",
      "Active voice required",
      "Under 12 words",
      "Must be unique across the deck",
      "No ending punctuation"
    ],
    "good_examples": [
      "Revenue grew 12% YoY driven by APAC expansion",
      "Three levers can reduce costs by $4.2M annually",
      "Customer churn declined for the third consecutive quarter"
    ],
    "bad_examples": [
      "Revenue Overview",
      "Cost Analysis",
      "Q3 Results"
    ]
  },

  "visual": {
    "ratio": "70% data/charts, 30% framing text",
    "typography_scale": "compact",
    "bullets_allowed": true,
    "icons_encouraged": true,
    "image_usage": "charts and diagrams only — no decorative photos",
    "colour_usage": "Black, white, one accent colour (typically blue). Minimal palette.",
    "chart_style": "Annotated, source-cited, insight-titled. Multi-series OK."
  },

  "preferred_intents": [
    "executive_summary", "kpi_dashboard", "comparison_columns",
    "data_table", "chart_driven", "matrix_2x2", "linear_process",
    "conclusion_cta"
  ],
  "discouraged_intents": [
    "image_showcase", "quote_testimonial"
  ],
  "forbidden_intents": [],

  "slide_structure": {
    "action_title": "Required — the main takeaway as a sentence",
    "subheading": "Optional — clarifies scope or angle",
    "body": "Charts, tables, or structured bullets backing up the title",
    "source_citation": "Required — bottom-left, small font"
  },

  "typical_slide_count": {
    "short": "10-15 slides for a focused recommendation",
    "standard": "30-50 slides with methodology and evidence",
    "with_appendix": "40-80 slides including backup materials"
  }
}
```

---

## The 8 Personas

### 1. strategy — Strategy Consulting
**Archetype:** McKinsey, BCG, Bain deliverable for C-suite decisions
**Narrative:** Pyramid Principle — conclusion first, MECE supporting arguments
**Density:** High — data-rich, 90 words max, 40%+ data slides
**Titles:** Assertive insight sentences ("Revenue grew 12% driven by APAC")
**Visual:** 70/30 data-to-text, compact typography, annotated charts with sources
**Bullets:** Yes, structured and evidence-backed
**Preferred intents:** exec_summary, kpi_dashboard, comparison, data_table, chart, matrix, process, conclusion
**Forbidden:** None
**Slide count:** 30–50 standard, 10–15 focused, up to 80 with appendix

### 2. executive — Executive Briefing
**Archetype:** Board deck, C-Suite review, investor update
**Narrative:** SCR (Situation → Complication → Resolution)
**Density:** Low — 60 words max, max 3 bullets, 4–8 slides total
**Titles:** Action-oriented ("Approve APAC Phase 2 expansion")
**Visual:** 50/50 data-to-text, large typography, bold KPI cards
**Bullets:** Minimal (3 max per slide), must be decisions or actions
**Preferred intents:** cover, executive_summary, kpi_dashboard, single_insight, conclusion_cta
**Discouraged:** data_table, org_chart, linear_process (too detailed for board level)
**Slide count:** 4–8 slides. Every slide must survive the "elevator test."

### 3. keynote — Conference Keynote / TED Talk
**Archetype:** TED, conference main stage, company all-hands
**Narrative:** Story arc (Setup → Tension → Resolution → Call to action)
**Density:** Minimal — 25 words max, one idea per slide
**Titles:** Provocative question or bold claim ("What if we could eliminate downtime entirely?")
**Visual:** 90/10 visual-to-text, dramatic typography, full-bleed images, no bullets
**Bullets:** Forbidden. Never use bullet points.
**Preferred intents:** single_insight, image_showcase, quote_testimonial, section_divider, cover, thank_you
**Discouraged:** data_table, comparison_columns, matrix_2x2 (too dense for stage)
**Forbidden:** Bullet-heavy slides of any kind
**Slide count:** 20–40 thin slides for 18-minute talk. One idea per slide.
**Special rules:** Dark backgrounds preferred. Sans-serif only. Font size never below 28pt equivalent. No source citations on-slide.

### 4. startup — Startup Pitch Deck
**Archetype:** Seed/Series A investor pitch, demo day, accelerator
**Narrative:** Problem → Solution → Market → Traction → Team → Ask
**Density:** Medium — 50 words max, 10-15 slides (Guy Kawasaki 10/20/30 rule)
**Titles:** Direct value propositions ("$4.2B market growing 23% annually")
**Visual:** 60/40 visual-to-text, clean and modern, product screenshots welcome
**Bullets:** Sparingly — prefer icons + short text pairs
**Preferred intents:** cover, single_insight, kpi_dashboard, comparison_columns, chart_driven, funnel, conclusion_cta, thank_you
**Discouraged:** data_table (too dense), org_chart (save for appendix)
**Slide count:** 10–15 slides. "Reading deck" can be 15–20 with more detail.
**Special rules:** Traction metrics must include context (MoM growth, not just absolute). Team slide required. Clear "ask" slide with amount and use of funds.

### 5. technical — Technical Review
**Archetype:** Architecture review, sprint retrospective, engineering deep-dive, design review
**Narrative:** Chronological or status-based (What we built → How it works → What's next)
**Density:** Medium-high — 80 words max, structured sections
**Titles:** Descriptive with context ("Sprint 14 delivered 42 story points, 12% above target")
**Visual:** 60/40 data-to-text, diagrams and flow charts, code snippets acceptable
**Bullets:** Yes, technical and structured
**Preferred intents:** linear_process, timeline, data_table, chart_driven, org_chart, comparison_columns, agenda, conclusion_cta
**Discouraged:** image_showcase, quote_testimonial, single_insight (too vague)
**Slide count:** 10–20 slides depending on scope.
**Special rules:** Monospace font for code/technical terms. Diagram-first approach. Architecture diagrams count as charts.

### 6. sales — Sales & Marketing
**Archetype:** Client pitch, product proposal, marketing review, competitive analysis
**Narrative:** Problem → Impact → Solution → Proof → Call to action
**Density:** Medium — 65 words max, 5 bullets max
**Titles:** Benefit-led ("Cut processing time by 60% with automated pipeline")
**Visual:** 50/50, polished and brand-forward, social proof prominent
**Bullets:** Yes, but prefer icon + text pairs or benefit statements
**Preferred intents:** cover, single_insight, comparison_columns, kpi_dashboard, funnel, quote_testimonial, before_after, conclusion_cta, thank_you
**Discouraged:** data_table (overwhelming for prospects), matrix_2x2 (too analytical)
**Slide count:** 10–20 slides. Demo or product slides should use screenshots.
**Special rules:** Competitor comparison must be factual. Social proof (logos, quotes, case studies) is high-value. Pricing slide optional but recommended.

### 7. workshop — Workshop / Training
**Archetype:** Training session, onboarding, skill-building workshop, tutorial
**Narrative:** Progressive disclosure (Overview → Foundation → Practice → Advanced → Recap)
**Density:** Medium — 70 words max, agenda-driven structure
**Titles:** Instructional and clear ("Step 3: Configure the data pipeline")
**Visual:** 50/50, step-by-step visuals, diagrams, screenshots
**Bullets:** Yes, numbered steps preferred over unordered lists
**Preferred intents:** cover, agenda, linear_process, comparison_columns, section_divider, conclusion_cta, thank_you
**Discouraged:** single_insight (too abstract for training), kpi_dashboard
**Slide count:** 20–40 slides for 1-hour session. Section dividers between modules.
**Special rules:** Each section should open with learning objective and close with key takeaway. Exercise/activity slides should be clearly marked. Handout-friendly layout.

### 8. academic — Academic / Research
**Archetype:** Conference paper, thesis defence, research seminar, lecture
**Narrative:** Scientific method (Background → Hypothesis → Method → Results → Discussion → Conclusion)
**Density:** Medium — 75 words max, structured with citations
**Titles:** Findings-focused ("Neural network outperforms baseline by 14% on benchmark X")
**Visual:** 60/40 data-to-text, precise charts with error bars, methodology diagrams
**Bullets:** Yes, structured and evidence-referenced
**Preferred intents:** cover, agenda, linear_process, data_table, chart_driven, comparison_columns, conclusion_cta, thank_you
**Discouraged:** image_showcase (unless results are visual), quote_testimonial, funnel
**Slide count:** 12–20 for conference (15-20 min), 40–60 for thesis defence.
**Special rules:** Citations on every data slide. Methodology must be replicable from slides alone. Error bars/confidence intervals required on quantitative results. Questions slide at end.

---

## Persona Registry Format

Personas follow the same registry model as packs and themes.

```json
// registry.json (excerpt)
{
  "personas": [
    {
      "id": "strategy",
      "name": "Strategy Consulting",
      "short": "McKinsey/BCG — data-rich, Pyramid, MECE",
      "url": "personas/strategy.json",
      "version": "1.0"
    },
    ...
  ]
}
```

Individual persona files are JSON matching the schema above, fetchable by Claude via `web_fetch`.

## How Personas Interact with Packs and Themes

```
User brief  →  Persona (how to communicate)
            →  Pack (which primitives to use)
            →  Theme (what colours/fonts)
            →  PISA generates deck
```

A persona can recommend specific packs:
- `strategy` persona recommends `corporate-essentials` or `finance-reporting` packs
- `keynote` persona recommends a future `keynote-visuals` pack
- `startup` persona recommends a future `startup-pitch` pack

But any combination works. You could use `keynote` persona with `finance-reporting` pack
to create a visually dramatic financial presentation.

## Tier 1 Usage

```
User: "Generate a Q3 board deck using executive persona"
Claude: [loads executive persona rules]
        [selects primitives matching preferred intents]
        [applies density overrides: max 60 words, max 3 bullets]
        [writes titles in action-oriented style]
        [limits to 4-8 slides]
        [renders with user's theme]

User: "List available personas"
Claude: [web_fetch registry.json]
        → Shows persona list with descriptions

User: "Switch to keynote persona"
Claude: [adjusts all generation parameters]
        "Now using keynote persona: one idea per slide, no bullets,
         dramatic typography, 20-40 thin slides."
```

## Tier 2 Usage

Same as Tier 1, plus:
- Personas stored locally in `data/personas/`
- Custom personas can be created and registered
- Persona rules are enforced by the quality engine during review (Workflow D)
- Export: personas included in `.pisa-collection` archives
