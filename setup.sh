#!/bin/bash
set -e

echo ""
echo "╔═══════════════════════════════════════════════════════╗"
echo "║   Claude Skills — Repository Setup                   ║"
echo "╚═══════════════════════════════════════════════════════╝"
echo ""

read -p "Your GitHub username: " GH_USER
if [ -z "$GH_USER" ]; then echo "❌ Empty username."; exit 1; fi

echo "→ Replacing YOUR_USERNAME with '$GH_USER'..."
find . -type f \( -name "*.md" -o -name "*.json" -o -name "*.yml" \) \
  -exec sed -i '' "s/YOUR_USERNAME/$GH_USER/g" {} \;
echo "  ✅ Done"

echo "→ Initializing git..."
git init
git add .
git commit -m "feat: initial release — PISA v1.0"
echo "  ✅ First commit created"

echo ""
echo "Now create the repo on GitHub:"
echo "  1. Go to https://github.com/new"
echo "  2. Name: claude-skills"
echo "  3. Public, NO README/gitignore/license"
echo "  4. Click 'Create repository'"
echo ""
read -p "Press ENTER after creating the empty repo..."

git remote add origin "https://github.com/$GH_USER/claude-skills.git"
git branch -M main
git push -u origin main

echo ""
echo "╔═══════════════════════════════════════════════════════╗"
echo "║  ✅ Live at github.com/$GH_USER/claude-skills"
echo "║                                                       ║"
echo "║  Registry URL for Claude:                             ║"
echo "║  https://raw.githubusercontent.com/$GH_USER/    "
echo "║    claude-skills/main/skills/pisa/registry/           ║"
echo "║    registry.json                                      ║"
echo "╚═══════════════════════════════════════════════════════╝"
echo ""
echo "Next: Settings → Pages (main /docs) → Discussions ✅ → Release v1.0.0"
