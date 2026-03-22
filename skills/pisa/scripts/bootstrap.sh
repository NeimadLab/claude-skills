#!/usr/bin/env bash
# ═══════════════════════════════════════════════════════════
# PISA Bootstrap — Local Development Setup
# Run from: claude-skills/skills/pisa/
# ═══════════════════════════════════════════════════════════
set -euo pipefail

RED='\033[0;31m'; GREEN='\033[0;32m'; YELLOW='\033[1;33m'; BLUE='\033[0;34m'; NC='\033[0m'
log(){ echo -e "${BLUE}[PISA]${NC} $1"; }
ok(){ echo -e "${GREEN}  ✅ $1${NC}"; }
warn(){ echo -e "${YELLOW}  ⚠  $1${NC}"; }
fail(){ echo -e "${RED}  ❌ $1${NC}"; exit 1; }

echo ""
echo -e "${BLUE}╔═══════════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║  PISA Bootstrap — Local Development Setup     ║${NC}"
echo -e "${BLUE}╚═══════════════════════════════════════════════╝${NC}"
echo ""

# ── Detect working directory ──
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
PISA_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"

if [ ! -f "$PISA_ROOT/SKILL.md" ]; then
  fail "Cannot find SKILL.md. Run this script from skills/pisa/ or via scripts/bootstrap.sh"
fi
log "PISA root: $PISA_ROOT"

# ── Step 1: Check Python ──
log "Step 1/7: Checking Python..."
if command -v python3 &>/dev/null; then
  PY_VER=$(python3 --version 2>&1 | awk '{print $2}')
  ok "Python $PY_VER"
else
  fail "Python 3 not found. Install Python 3.10+ from python.org"
fi

# ── Step 2: Check Node.js ──
log "Step 2/7: Checking Node.js..."
if command -v node &>/dev/null; then
  NODE_VER=$(node --version)
  ok "Node.js $NODE_VER"
else
  fail "Node.js not found. Install Node.js 18+ from nodejs.org"
fi

# ── Step 3: Install Python dependencies ──
log "Step 3/7: Installing Python dependencies..."
pip3 install python-pptx numpy scipy scikit-learn --quiet 2>/dev/null \
  || pip3 install python-pptx numpy scipy scikit-learn --break-system-packages --quiet 2>/dev/null \
  || fail "pip install failed"
ok "python-pptx, numpy, scipy, scikit-learn"

# ── Step 4: Install Node.js dependencies ──
log "Step 4/7: Installing Node.js dependencies..."
cd "$PISA_ROOT"
if [ ! -d node_modules/pptxgenjs ]; then
  npm install pptxgenjs --save --silent 2>/dev/null || fail "npm install failed"
fi
ok "pptxgenjs"

# ── Step 5: Validate Python modules ──
log "Step 5/7: Validating Python modules..."
cd "$PISA_ROOT"
python3 -m py_compile services/extraction/extract_engine.py && ok "extract_engine.py" || fail "extract_engine.py won't compile"
python3 -m py_compile services/svg/canvas_to_svg.py && ok "canvas_to_svg.py" || fail "canvas_to_svg.py won't compile"
python3 -m py_compile services/qa/programmatic_qa.py && ok "programmatic_qa.py" || fail "programmatic_qa.py won't compile"

# ── Step 6: Quick self-test ──
log "Step 6/7: Running self-test..."
cd "$PISA_ROOT"
python3 -c "
import sys, os
sys.path.insert(0, '.')
os.chdir('$(echo $PISA_ROOT)')

# Test SVG renderer
from services.svg.canvas_to_svg import render_svg, NEUTRAL_THEME
test_prim = {
    'intent': 'kpi_dashboard', 'layout_type': 'grid', 'quality_score': 8.0,
    'semantic_groups': [], 'zones': [], 'components': [
        {'role': 'title', 'x_pct': 3, 'y_pct': 3, 'w_pct': 94, 'h_pct': 10,
         'text_preview': 'Test', 'visual': {'bg_variant': 'dark'}},
        {'role': 'kpi_card', 'x_pct': 3, 'y_pct': 16, 'w_pct': 30, 'h_pct': 35,
         'kpi': {'value': '42', 'unit': '%', 'label': 'TEST METRIC'},
         'visual': {'bg_variant': 'light', 'has_separator': True}}
    ]
}
svg = render_svg(test_prim, NEUTRAL_THEME)
assert len(svg) > 500, 'SVG too short'
print('  SVG renderer: OK')

# Test QA module loads
from services.qa.programmatic_qa import qa_canvas
issues = qa_canvas(test_prim)
print(f'  QA engine: OK ({len(issues)} info items on test canvas)')
" || fail "Self-test failed"
ok "Self-test passed"

# ── Step 7: Registry status ──
log "Step 7/7: Registry status..."
cd "$PISA_ROOT"
python3 -c "
import json, os
os.chdir('registry')
reg = json.load(open('registry.json'))
packs = reg.get('packs', [])
themes = [f for f in os.listdir('themes') if f.endswith('.json')] if os.path.isdir('themes') else []
personas = [f for f in os.listdir('personas') if f.endswith('.json')] if os.path.isdir('personas') else []
total_prims = 0
for p in packs:
    if os.path.exists(p['url']):
        pack = json.load(open(p['url']))
        total_prims += len(pack['canvases'])
print(f'  Packs: {len(packs)} ({total_prims} canvases)')
print(f'  Themes: {len(themes)}')
print(f'  Personas: {len(personas)}')
"

echo ""
echo -e "${GREEN}╔═══════════════════════════════════════════════╗${NC}"
echo -e "${GREEN}║  ✅ PISA local environment ready               ║${NC}"
echo -e "${GREEN}║                                                ║${NC}"
echo -e "${GREEN}║                                                ║${NC}"
echo -e "${GREEN}║  Full docs:                                    ║${NC}"
echo -e "${GREEN}║    docs/tier2-setup.md                         ║${NC}"
echo -e "${GREEN}╚═══════════════════════════════════════════════╝${NC}"
echo ""
