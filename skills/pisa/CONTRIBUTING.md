# Contributing to PISA

This covers PISA-specific contribution rules. For general repo guidelines, see the [root CONTRIBUTING.md](../../CONTRIBUTING.md).

## Submitting a Pack

1. Extract canvases from your deck using PISA Workflow A
2. Ask Claude: `"Export the library as a pack JSON called my-pack"`
3. Validate — every canvas must have:
   - `schema_version: 2.1`
   - `quality_score >= 7.0`
   - `kpi{}` on all KPI card components
   - `visual{}` on all components
   - Embedded SVG preview
4. Add the file to `registry/packs/`
5. Add an entry to `registry/registry.json`
6. Open a PR

## Submitting a Theme

Create a JSON file mapping all required token anchors:
```
token.color.primary, .secondary, .accent, .background, .text,
.text.muted, .border, .surface, .success, .warning, .danger
token.font.heading, .body
```

Add to `registry/themes/` and update `registry/registry.json`.

## Submitting a Persona

Follow the JSON schema in `references/pisa-personas.md`. Required fields: `persona_id`, `name`, `density`, `titles`, `preferred_intents`. Add to `registry/personas/` and update `registry/registry.json`.

## Improving the Skill Code

Changes to SKILL.md, the extraction engine, SVG renderer, or QA engine are welcome. Test by running the relevant Python/JS scripts. All Python modules must compile cleanly.
