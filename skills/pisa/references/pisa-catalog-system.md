# PISA Template Catalog System

## Purpose

The catalog provides a visual, filterable interface to the template library. Instead
of reading JSON coordinates, users see rendered thumbnails and filter by intent, quality,
tag, source deck, or layout type.

---

## Architecture

```
┌──────────────────────────────────────────────┐
│  Catalog Index (catalog_index.json)          │
│  ├── Per-template: id, intent, quality,     │
│  │   layout, tags, thumbnail path, status    │
│  └── Aggregates: intent distribution,        │
│      quality histogram, total count          │
├──────────────────────────────────────────────┤
│  Thumbnails (data/thumbnails/)               │
│  ├── {template_id}.svg (1920x1080)          │
│  └── {template_id}_thumb.svg (480x270)      │
├──────────────────────────────────────────────┤
│  Multi-theme Previews (data/previews/)       │
│  ├── {template_id}_corporate.svg            │
│  ├── {template_id}_light.svg                │
│  └── {template_id}_dark.svg                 │
└──────────────────────────────────────────────┘
```

## Catalog Index

Rebuilt on every library mutation (add, version, remove). Lightweight JSON index
that can be loaded without parsing every template.

```python
import json, os, datetime

def rebuild_catalog_index(library_path="pisa_library.json",
                          thumbnail_dir="data/thumbnails",
                          output_path="catalog_index.json"):
    """Rebuild the catalog index from the current library state."""
    with open(library_path) as f:
        library = json.load(f)

    entries = []
    intent_dist = {}
    quality_buckets = {"excellent": 0, "good": 0, "fair": 0, "draft": 0}

    for prim in library["templates"]:
        pid = prim["id"]
        q = prim.get("quality_score", 0)
        intent = prim["intent"]
        intent_dist[intent] = intent_dist.get(intent, 0) + 1

        if q >= 8.0:   quality_buckets["excellent"] += 1
        elif q >= 6.0: quality_buckets["good"] += 1
        elif q >= 4.0: quality_buckets["fair"] += 1
        else:          quality_buckets["draft"] += 1

        thumb = os.path.join(thumbnail_dir, f"{pid}.svg")
        thumb_small = os.path.join(thumbnail_dir, f"{pid}_thumb.svg")

        entries.append({
            "id": pid,
            "intent": intent,
            "intent_confidence": prim.get("intent_confidence", 0),
            "layout_type": prim.get("layout_type", "unknown"),
            "quality_score": q,
            "status": prim.get("status", "draft"),
            "version": prim.get("version", 1),
            "component_count": len(prim.get("components", [])),
            "word_count": prim.get("density", {}).get("total_words", 0),
            "source_file": prim.get("source", {}).get("file", ""),
            "source_slide": prim.get("source", {}).get("slide", 0),
            "tags": prim.get("tags", []),
            "thumbnail": thumb if os.path.exists(thumb) else None,
            "thumbnail_small": thumb_small if os.path.exists(thumb_small) else None,
            "extracted_at": prim.get("source", {}).get("extracted_at", ""),
        })

    index = {
        "catalog_version": 1,
        "rebuilt_at": datetime.datetime.now().isoformat(),
        "total_templates": len(entries),
        "intent_distribution": intent_dist,
        "quality_distribution": quality_buckets,
        "entries": entries,
    }

    with open(output_path, "w") as f:
        json.dump(index, f, indent=2)

    return index
```

## Thumbnail Generation (Enhanced)

Two sizes: full (1920x1080) for detail view, small (480x270) for grid browsing.

```python
from SVG string import Image
import subprocess, os

def generate_thumbnails(template, theme, thumbnail_dir="data/thumbnails"):
    """Generate full + small thumbnails for a template."""
    os.makedirs(thumbnail_dir, exist_ok=True)
    pid = template["id"]

    # 1. Render to PPTX
    tmp_pptx = f"/tmp/pisa_thumb_{pid}.pptx"
    render_data = json.dumps({"template": template, "theme": theme})
    render_file = f"/tmp/pisa_render_{pid}.json"
    with open(render_file, "w") as f:
        f.write(render_data)

    result = subprocess.run(
        ["node", "apps/renderer-node/render.js", "--input", render_file, "--output", tmp_pptx],
        capture_output=True, text=True
    )
    if result.returncode != 0:
        return {"error": f"Render failed: {result.stderr[:200]}"}

    # 2. Convert to PNG (full resolution)
    subprocess.run(
        ["svg_renderer", "--headless", "--convert-to", "png", "--outdir", "/tmp", tmp_pptx],
        capture_output=True
    )

    src_png = f"/tmp/pisa_thumb_{pid}.svg"
    full_path = os.path.join(thumbnail_dir, f"{pid}.svg")
    small_path = os.path.join(thumbnail_dir, f"{pid}_thumb.svg")

    if not os.path.exists(src_png):
        return {"error": "LibreOffice conversion failed"}

    # 3. Full size (ensure 1920x1080)
    img = Image.open(src_png)
    img_resized = img.resize((1920, 1080), Image.LANCZOS)
    img_resized.save(full_path, "PNG")

    # 4. Small thumbnail (480x270)
    img_small = img.resize((480, 270), Image.LANCZOS)
    img_small.save(small_path, "PNG")

    # Cleanup
    for f in [tmp_pptx, render_file, src_png]:
        if os.path.exists(f):
            os.remove(f)

    return {"full": full_path, "small": small_path}
```

## Multi-Theme Preview

Render a template in multiple themes for side-by-side comparison.

```python
def generate_multi_theme_preview(template, themes_dict, preview_dir="data/previews"):
    """Render a template in each theme. themes_dict = {"name": theme_json, ...}"""
    os.makedirs(preview_dir, exist_ok=True)
    pid = template["id"]
    results = {}

    for theme_name, theme in themes_dict.items():
        render_data = json.dumps({"template": template, "theme": theme})
        render_file = f"/tmp/pisa_preview_{pid}_{theme_name}.json"
        tmp_pptx = f"/tmp/pisa_preview_{pid}_{theme_name}.pptx"

        with open(render_file, "w") as f:
            f.write(render_data)

        r = subprocess.run(
            ["node", "apps/renderer-node/render.js", "--input", render_file, "--output", tmp_pptx],
            capture_output=True, text=True
        )
        if r.returncode != 0:
            results[theme_name] = {"error": r.stderr[:200]}
            continue

        subprocess.run(
            ["svg_renderer", "--headless", "--convert-to", "png", "--outdir", "/tmp", tmp_pptx],
            capture_output=True
        )

        src = f"/tmp/pisa_preview_{pid}_{theme_name}.svg"
        dest = os.path.join(preview_dir, f"{pid}_{theme_name}.svg")
        if os.path.exists(src):
            img = Image.open(src).resize((960, 540), Image.LANCZOS)
            img.save(dest, "PNG")
            results[theme_name] = dest
        else:
            results[theme_name] = {"error": "Conversion failed"}

        # Cleanup
        for f in [render_file, tmp_pptx, src]:
            if os.path.exists(f):
                os.remove(f)

    return results
```

## Catalog Query

```python
def query_catalog(index_path="catalog_index.json", intent=None, min_quality=0,
                  layout_type=None, status=None, tag=None, source=None, limit=20):
    """Filter catalog entries. Returns sorted by quality descending."""
    with open(index_path) as f:
        index = json.load(f)

    results = index["entries"]

    if intent:
        results = [e for e in results if e["intent"] == intent]
    if min_quality > 0:
        results = [e for e in results if e["quality_score"] >= min_quality]
    if layout_type:
        results = [e for e in results if e["layout_type"] == layout_type]
    if status:
        results = [e for e in results if e["status"] == status]
    if tag:
        results = [e for e in results if tag in e.get("tags", [])]
    if source:
        results = [e for e in results if source.lower() in e.get("source_file", "").lower()]

    results.sort(key=lambda e: -e["quality_score"])
    return results[:limit]
```

## CLI Usage

```bash
# Rebuild catalog index
python3 scripts/library/catalog.py rebuild

# Browse by intent (returns entries with thumbnail paths)
python3 scripts/library/catalog.py query --intent kpi_dashboard

# Browse high-quality only
python3 scripts/library/catalog.py query --min-quality 7.0

# Generate multi-theme previews for a template
python3 scripts/library/catalog.py preview --id prim_deck_3_a8f2 --themes corporate,light,dark

# Full catalog summary
python3 scripts/library/catalog.py summary
```
