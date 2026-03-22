# Personas — Communication Strategies

A persona controls **how** the deck communicates. It is not a theme (colors/fonts) — it is a generation strategy that affects template selection, density limits, title style, narrative framework, and visual ratio.

Selecting a persona before generation is the single highest-impact decision for deck quality.

## The Eight Personas

### strategy — McKinsey / BCG
- **Density:** High (90 words, 5 bullets, 7 shapes)
- **Narrative:** Pyramid, MECE — executive summary with 3-5 findings up front
- **Titles:** Full insight sentences, active voice, under 12 words
- **Key rule:** 40%+ data slides. Source citations required.
- **Typical:** 30-50 slides (10-15 short)

### executive — Board / C-Suite
- **Density:** Low (60 words, 3 bullets, 5 shapes)
- **Narrative:** Situation → Complication → Resolution
- **Titles:** Action-oriented statements, under 10 words
- **Key rule:** 4-8 slides. Elevator test. Every slide earns its place.
- **Typical:** 4-8 slides

### keynote — TED / Conference
- **Density:** Minimal (25 words, 0 bullets, 3 shapes)
- **Narrative:** Story arc — hook, tension, resolution
- **Titles:** Bold claims or provocative questions, under 8 words
- **Key rule:** One idea per slide. 90% visual. Font ≥28pt. Bullets forbidden.
- **Typical:** 20-40 slides

### startup — Seed / Series A
- **Density:** Medium (50 words, 4 bullets)
- **Narrative:** Problem → Solution → Market → Traction → Team → Ask
- **Titles:** Direct value proposition with numbers
- **Key rule:** 10-15 slides. 10/20/30 rule. Team slide. Clear ask with amount.
- **Typical:** 10-15 slides

### technical — Architecture / Sprint
- **Density:** Medium-high (80 words, 5 bullets)
- **Narrative:** Chronological — status, details, next steps
- **Titles:** Descriptive with metrics and context
- **Key rule:** Diagrams first. Monospace for code. Include timeline.
- **Typical:** 10-20 slides

### sales — Pitch / Proposal
- **Density:** Medium (65 words, 5 bullets)
- **Narrative:** Problem → Proof → CTA
- **Titles:** Benefit-led with impact numbers
- **Key rule:** Social proof (quotes, logos). Clear CTA on final slide.
- **Typical:** 10-20 slides

### workshop — Training
- **Density:** Medium (70 words, 5 bullets)
- **Narrative:** Progressive disclosure — build complexity gradually
- **Titles:** Instructional with step references
- **Key rule:** Learning objectives per section. Numbered steps. Recap slides.
- **Typical:** 20-40 slides

### academic — Conference / Thesis
- **Density:** Medium (75 words, 5 bullets)
- **Narrative:** Scientific method — background, method, results, discussion
- **Titles:** State the finding with quantitative result
- **Key rule:** Citations required. Error bars on data. Methodology transparent.
- **Typical:** 12-20 (conference), 40-60 (thesis)

## Using Personas

Tell Claude which persona to use before generating:

```
Create a 10-slide deck about our Q3 results using the executive persona
```

Or switch mid-session:

```
Switch to the keynote persona and rebuild slides 3-8
```

Personas are JSON files in the registry. Install custom ones:

```
Install the strategy persona from my registry
```
