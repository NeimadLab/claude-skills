# PISA Registry — Complete GitHub Repository Setup Guide

## What This Repository Is

A PISA registry is a GitHub repository that serves as the distribution hub for slide templates, themes, and personas. Claude fetches content via raw URLs. No server, no database — just JSON files in a Git repo.

It also serves as: a visual catalog via GitHub Pages, a collaboration hub (PRs for packs), and a version-controlled library.

---

## Step 1 — Create the Repository

1. **github.com** → **+** → **New repository**
2. Name: `pisa-registry`, Public, ✅ README, License: MIT
3. Clone: `git clone https://github.com/NeimadLab/pisa-registry.git`

---

## Step 2 — Directory Structure

```bash
mkdir -p packs themes personas docs/catalog assets/previews .github/workflows .github/ISSUE_TEMPLATE
```

```
pisa-registry/
├── registry.json              ← Master index (Claude fetches first)
├── packs/                     ← Template collections
│   ├── corporate-essentials.json
│   ├── finance-reporting.json
│   ├── strategy-consulting.json
│   ├── startup-pitch.json
│   └── my-custom-pack.json
├── themes/                    ← Design token sets
│   ├── corporate_dark.json
│   ├── corporate_light.json
│   └── my_brand.json
├── personas/                  ← Communication strategies
│   ├── strategy.json
│   ├── executive.json
│   ├── keynote.json
│   └── ... (8 total)
├── docs/                      ← GitHub Pages site
│   ├── index.md               ← Landing page
│   ├── catalog.md             ← Visual pack catalog
│   ├── getting-started.md     ← Quick start
│   ├── creating-packs.md      ← How to contribute
│   ├── _config.yml            ← Jekyll config
│   └── catalog/               ← SVG preview images
│       ├── corporate-essentials.svg
│       └── finance-reporting.svg
├── assets/previews/           ← PNG preview grids for README
├── .github/
│   ├── workflows/
│   │   └── validate.yml       ← CI: validate JSON on every PR
│   └── ISSUE_TEMPLATE/
│       ├── pack-request.md
│       └── bug-report.md
├── README.md
├── CONTRIBUTING.md
├── CHANGELOG.md
├── LICENSE
└── .gitignore
```

---

## Step 3 — registry.json (Master Index)

```json
{
  "registry_version": 1,
  "schema_version": "2.1",
  "updated": "2026-03-21",
  "base_url": "https://raw.githubusercontent.com/NeimadLab/pisa-registry/main",
  "packs": [
    {
      "id": "corporate-essentials",
      "name": "Corporate Essentials",
      "description": "Full 21-intent coverage for corporate presentations",
      "templates": 24, "intents_covered": 21, "quality_min": 7.0,
      "themes_included": ["corporate_dark", "corporate_light"],
      "recommended_personas": ["strategy", "executive"],
      "url": "packs/corporate-essentials.json",
      "version": "1.0", "author": "YOUR_NAME"
    }
  ],
  "themes": [
    {"id": "corporate_dark", "name": "Corporate Dark",
     "url": "themes/corporate_dark.json", "version": "1.0"}
  ],
  "personas": [
    {"id": "strategy", "name": "Strategy Consulting",
     "url": "personas/strategy.json", "version": "1.0"}
  ]
}
```

---

## Step 4 — README.md

Should contain: project description, quick start (one command to install a pack), table of available packs/themes/personas, link to visual catalog on GitHub Pages, link to CONTRIBUTING.md.

Quick start section:
```
In Claude, say:
> Use my PISA registry at
> https://raw.githubusercontent.com/NeimadLab/pisa-registry/main/registry.json

Then: "Install the corporate essentials pack"
→ 24 templates loaded. Ready to generate.
```

---

## Step 5 — CONTRIBUTING.md

Three contribution paths:

**Adding a pack:** Extract templates from reference deck → ask Claude to export as pack JSON → validate (schema 2.1, quality ≥7.0, kpi{} on KPI cards, visual{} on all components, embedded SVGs) → add to packs/ → update registry.json → open PR.

**Adding a theme:** Create JSON with all 25 token anchors → add to themes/ → update registry.json → open PR.

**Adding a persona:** Follow persona schema → add to personas/ → update registry.json → open PR.

---

## Step 6 — GitHub Pages (Visual Catalog)

### Enable Pages
Settings → Pages → Source: Deploy from branch → Branch: main, Folder: /docs → Save.

Site URL: `https://NeimadLab.github.io/pisa-registry/`

### docs/_config.yml
```yaml
title: PISA Registry
description: Slide template packs, themes, and personas
theme: minima
baseurl: /pisa-registry
url: https://NeimadLab.github.io
```

### docs/index.md
Landing page with: pack list + descriptions, link to catalog, installation instructions, link to GitHub repo.

### docs/catalog.md
Embeds SVG grid previews for each pack. Generate these in Claude: "Generate SVG catalog grids for all packs" → save as docs/catalog/pack-name.svg.

---

## Step 7 — CI Validation (.github/workflows/validate.yml)

```yaml
name: Validate Registry
on:
  push:
    branches: [main]
  pull_request:
    branches: [main]
jobs:
  validate:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: Validate all JSON
        run: |
          python3 -c "import json; json.load(open('registry.json'))"
          for f in packs/*.json; do
            python3 -c "
          import json
          pack = json.load(open('$f'))
          for p in pack['templates']:
              assert p.get('quality_score',0) >= 7.0, f'{p[\"id\"]} quality < 7.0'
              for c in p.get('components',[]):
                  if c['role']=='kpi_card': assert c.get('kpi'), f'KPI missing kpi{{}}'
          print(f'  OK $f: {len(pack[\"templates\"])} templates')
          "
          done
          for f in themes/*.json; do
            python3 -c "
          import json; t=json.load(open('$f'))
          for k in ['token.color.primary','token.color.text','token.font.heading']:
              assert k in t, f'$f missing {k}'
          print(f'  OK $f')
          "
          done
```

---

## Step 8 — Issue Templates

### .github/ISSUE_TEMPLATE/pack-request.md
Fields: pack name, target audience, estimated templates, intents needed (checklist), reference material available?

### .github/ISSUE_TEMPLATE/bug-report.md
Fields: pack/theme/persona name, version, issue description, steps to reproduce, expected behavior.

---

## Step 9 — Push Everything

```bash
git add .
git commit -m "Initial registry: 4 packs, 3 themes, 8 personas"
git push origin main
```

Your raw URL: `https://raw.githubusercontent.com/NeimadLab/pisa-registry/main/registry.json`

---

## Adding Your Own Content

### From Extracted Decks
1. Upload PPTX to Claude → "Extract all slides as PISA templates"
2. Review → "Export the library as a pack JSON called my-custom-pack"
3. Download → copy to `packs/my-custom-pack.json`
4. Update registry.json → commit → push

### From Scratch
Ask Claude: "Create a PISA pack with 10 templates for [use case]"
Download → add to registry → push.

---

## Private Registries

**Option A — Fine-grained token:** github.com/settings/tokens → Generate → Repository: your registry → Contents: Read-only. Provide token to Claude.

**Option B — Upload workflow:** Download files manually, upload to Claude. No token needed.

**Option C — GitHub Actions artifact:** Publish packs as workflow artifacts. Team downloads without repo access.

---

## Team Setup

### Shared Registry (Recommended)
One repo, multiple contributors via PRs. CI validates automatically. Everyone uses the same registry URL.

### Per-Team Structure
```
company-pisa-registry/
├── packs/
│   ├── team-engineering/
│   ├── team-finance/
│   └── team-marketing/
├── themes/
│   └── company-brand.json    ← Shared
└── personas/
    └── company-default.json  ← Shared
```

---

## Version Management

Semantic versioning: 1.0 → initial, 1.1 → new templates, 2.0 → breaking schema change. Update version in both the content file and registry.json. Claude detects version changes on "check for updates".

Keep a CHANGELOG.md at repo root documenting what changed in each version.
