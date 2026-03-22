# Tier 2 — Local Development Setup

## Tier 1 vs Tier 2

| | Tier 1 (Claude-native) | Tier 2 (Local) |
|---|---|---|
| **Setup** | Drop SKILL.md into a Claude Project | Clone repo + run bootstrap |
| **Library** | Session-ephemeral (export/import JSON) | Persistent on disk |
| **Dependencies** | Claude installs them in sandbox | You install them locally |
| **Best for** | Using PISA in Claude conversations | Developing PISA, running scripts locally, CI/CD pipelines |

Most users only need Tier 1. Tier 2 is for contributors, developers, and automation.

## Prerequisites

- Python 3.10+
- Node.js 18+
- Git

## Setup

```bash
# Clone the repo
git clone https://github.com/NeimadLab/claude-skills.git
cd claude-skills/skills/pisa

# Run bootstrap
bash scripts/bootstrap.sh
```

The bootstrap script:
1. Verifies Python and Node.js versions
2. Installs Python dependencies (python-pptx, numpy, scipy, scikit-learn)
3. Installs Node.js dependencies (pptxgenjs)
4. Validates the extraction engine compiles
5. Validates the SVG renderer compiles
6. Validates the QA engine compiles
7. Runs a quick self-test
8. Reports the registry status (packs, themes, personas)

## What You Can Do Locally

### Run the extraction engine

```bash
cd skills/pisa
python3 -c "
from services.extraction.extract_engine import deep_inventory
from pptx import Presentation
prs = Presentation('path/to/deck.pptx')
for i, slide in enumerate(prs.slides):
    shapes = deep_inventory(slide, i)
    print(f'Slide {i+1}: {len(shapes)} shapes')

"
```

### Generate SVG previews

```bash
python3 -c "
import json
from services.svg.canvas_to_svg import render_svg
prim = json.load(open('registry/packs/corporate-essentials.json'))['canvases'][0]
svg = render_svg(prim)
open('preview.svg', 'w').write(svg)
print('Preview saved')
"
```

### Run QA on a generated PPTX

```bash
python3 -c "
from services.qa.programmatic_qa import qa_deck
result = qa_deck('output.pptx')
for issue in result['all_issues']:
    print(f\"{issue['severity']}: {issue['detail']}\")
print(f\"Result: {result['summary']['verdict']}\")
"
```

### Validate the registry

```bash
python3 -c "
import json, os
os.chdir('registry')
reg = json.load(open('registry.json'))
for p in reg['packs']:
    pack = json.load(open(p['url']))
    print(f\"{p['id']}: {len(pack['canvases'])} canvases\")
"
```
