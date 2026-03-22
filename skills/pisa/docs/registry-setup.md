# Registry Setup

The PISA registry is a collection of JSON files served via raw GitHub URLs. Claude fetches them at runtime with `web_fetch`. No server, no API.

## Registry URL

```
https://raw.githubusercontent.com/NeimadLab/claude-skills/main/skills/pisa/registry/registry.json
```

## Structure

```
registry/
├── registry.json            ← Master index
├── packs/
│   ├── corporate-essentials.json   (24 primitives)
│   ├── finance-reporting.json      (14 primitives)
│   ├── strategy-consulting.json    (12 primitives)
│   └── startup-pitch.json          (11 primitives)
├── themes/
│   ├── corporate_dark.json
│   ├── corporate_light.json
│   └── finance_dark.json
└── personas/
    ├── strategy.json
    ├── executive.json
    └── ... (8 total)
```

## How It Works

1. User says: "Install the finance pack"
2. Claude fetches `registry.json` → finds the pack entry
3. Claude fetches `packs/finance-reporting.json` via the `base_url` + relative path
4. Primitives merge into the session library
5. Included themes are loaded

## Adding Your Own Packs

1. Extract primitives from your deck (Workflow A)
2. Export: `"Export the library as a pack JSON called my-pack"`
3. Add the file to `registry/packs/`
4. Add an entry to `registry/registry.json`
5. Commit and push

Your pack is now installable: `"Install my-pack"`

## registry.json Format

```json
{
  "registry_version": 1,
  "schema_version": "2.1",
  "base_url": "https://raw.githubusercontent.com/.../registry",
  "packs": [
    {
      "id": "my-pack",
      "name": "My Custom Pack",
      "description": "Extracted from our brand deck",
      "primitives": 15,
      "url": "packs/my-pack.json",
      "version": "1.0"
    }
  ],
  "themes": [ ... ],
  "personas": [ ... ]
}
```

## Quality Requirements for Packs

- Schema version 2.1
- Quality score ≥ 7.0 on every primitive
- `kpi{}` on all KPI card components
- `visual{}` on all components
- Embedded SVG preview

CI validates these automatically on every push.
