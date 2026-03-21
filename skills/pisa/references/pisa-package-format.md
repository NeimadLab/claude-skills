# PISA Package Format (.pisa)

## Purpose

A `.pisa` file is a self-contained, portable primitive exchange unit. It bundles
everything needed to import a slide primitive into any PISA library: the primitive
JSON, a rendered thumbnail, the theme it was extracted with, and provenance metadata.

## Structure

A `.pisa` file is a ZIP archive with this layout:

```
my_primitive.pisa
├── manifest.json          # Package metadata, schema version, dependencies
├── primitive.json         # The V2 primitive (components, roles, tokens, groups)
├── thumbnail.svg          # 1920x1080 rendered preview (neutral or source theme)
├── theme.json             # Theme used at extraction time (for re-rendering)
└── provenance.json        # Source file, extractor version, extraction date, author
```

## manifest.json

```json
{
  "pisa_package_version": 1,
  "primitive_schema_version": 2,
  "id": "prim_quarterly_3_a8f2c1d9e4b7",
  "intent": "kpi_dashboard",
  "quality_score": 7.5,
  "layout_type": "grid",
  "component_count": 5,
  "word_count": 42,
  "tags": ["finance", "KPI", "quarterly"],
  "author": "dom",
  "created_at": "2026-03-21T10:00:00Z",
  "description": "KPI dashboard with 4 metric cards and trend arrows",
  "dependencies": {
    "min_pisa_version": "2.0",
    "renderer": "pptxgenjs"
  },
  "checksum": "sha256:abc123..."
}
```

## Collection Format (.pisa-collection)

For exporting multiple primitives (e.g., an entire library or an intent family):

```
my_collection.pisa-collection
├── collection.json         # Index of all primitives with metadata
├── primitives/
│   ├── prim_001.pisa
│   ├── prim_002.pisa
│   └── ...
└── themes/
    ├── corporate_dark.json
    └── corporate_light.json
```

### collection.json

```json
{
  "pisa_collection_version": 1,
  "name": "Corporate Slide Library",
  "description": "Validated primitives for corporate brand presentations",
  "primitive_count": 24,
  "intent_coverage": {
    "cover": 2, "executive_summary": 3, "kpi_dashboard": 4,
    "comparison_columns": 3, "linear_process": 2, "timeline": 2,
    "matrix_2x2": 1, "single_insight": 2, "section_divider": 1,
    "conclusion_cta": 2, "agenda": 1, "thank_you": 1
  },
  "themes_included": ["corporate_dark", "corporate_light"],
  "created_at": "2026-03-21T10:00:00Z",
  "author": "dom"
}
```

---

## Operations

### Export a single primitive

```python
import zipfile, json, os, hashlib

def export_pisa(primitive, theme, thumbnail_path, output_path, author="anonymous", tags=None):
    """Export a primitive as a .pisa package."""
    manifest = {
        "pisa_package_version": 1,
        "primitive_schema_version": primitive.get("schema_version", 2),
        "id": primitive["id"],
        "intent": primitive["intent"],
        "quality_score": primitive.get("quality_score", 0),
        "layout_type": primitive.get("layout_type", "unknown"),
        "component_count": len(primitive.get("components", [])),
        "word_count": primitive.get("density", {}).get("total_words", 0),
        "tags": tags or [],
        "author": author,
        "created_at": primitive.get("source", {}).get("extracted_at", ""),
        "description": "",
        "dependencies": {"min_pisa_version": "2.0", "renderer": "pptxgenjs"},
    }

    # Compute checksum
    prim_bytes = json.dumps(primitive, sort_keys=True).encode()
    manifest["checksum"] = f"sha256:{hashlib.sha256(prim_bytes).hexdigest()}"

    provenance = {
        "source_file": primitive.get("source", {}).get("file"),
        "source_slide": primitive.get("source", {}).get("slide"),
        "extractor": primitive.get("source", {}).get("extractor"),
        "extracted_at": primitive.get("source", {}).get("extracted_at"),
        "author": author,
        "version": primitive.get("version", 1),
    }

    with zipfile.ZipFile(output_path, "w", zipfile.ZIP_DEFLATED) as zf:
        zf.writestr("manifest.json", json.dumps(manifest, indent=2))
        zf.writestr("primitive.json", json.dumps(primitive, indent=2))
        zf.writestr("theme.json", json.dumps(theme, indent=2))
        zf.writestr("provenance.json", json.dumps(provenance, indent=2))
        if thumbnail_path and os.path.exists(thumbnail_path):
            zf.write(thumbnail_path, "thumbnail.svg")

    return output_path


### Import a .pisa package

def import_pisa(pisa_path, library_path="pisa_library.json",
                thumbnail_dir="data/thumbnails", mode="add"):
    """Import a .pisa package into the library.
    Returns: registration result dict."""
    import zipfile

    with zipfile.ZipFile(pisa_path, "r") as zf:
        manifest = json.loads(zf.read("manifest.json"))
        primitive = json.loads(zf.read("primitive.json"))
        # theme = json.loads(zf.read("theme.json"))  # available if needed

        # Validate schema version
        if manifest.get("primitive_schema_version", 1) > 2:
            return {"action": "rejected",
                    "reason": f"Schema version {manifest['primitive_schema_version']} "
                              f"not supported (max: 2)"}

        # Verify checksum
        prim_bytes = json.dumps(primitive, sort_keys=True).encode()
        expected = f"sha256:{hashlib.sha256(prim_bytes).hexdigest()}"
        if manifest.get("checksum") and manifest["checksum"] != expected:
            return {"action": "rejected", "reason": "Checksum mismatch — file may be corrupted"}

        # Extract thumbnail
        if "thumbnail.svg" in zf.namelist():
            os.makedirs(thumbnail_dir, exist_ok=True)
            thumb_path = os.path.join(thumbnail_dir, f"{primitive['id']}.png")
            with open(thumb_path, "wb") as f:
                f.write(zf.read("thumbnail.svg"))

    # Register using standard V2 registration (handles dedup + versioning)
    # Import from extract_engine to avoid circular deps
    from sub_skills.slide_to_primitive.extract_engine import register_primitive_v2
    return register_primitive_v2(primitive, library_path, mode)


### Batch export (collection)

def export_collection(library_path, output_path, themes=None,
                      thumbnail_dir="data/thumbnails", author="anonymous",
                      name="PISA Library Export"):
    """Export entire library as a .pisa-collection."""
    with open(library_path) as f:
        library = json.load(f)

    os.makedirs("/tmp/pisa_export", exist_ok=True)

    # Export each primitive as .pisa
    pisa_files = []
    intent_coverage = {}
    for prim in library["primitives"]:
        intent = prim["intent"]
        intent_coverage[intent] = intent_coverage.get(intent, 0) + 1

        thumb = os.path.join(thumbnail_dir, f"{prim['id']}.png")
        theme = themes.get(prim.get("source", {}).get("file"), {}) if themes else {}
        pisa_file = f"/tmp/pisa_export/{prim['id']}.pisa"
        export_pisa(prim, theme, thumb if os.path.exists(thumb) else None,
                    pisa_file, author)
        pisa_files.append(pisa_file)

    collection_meta = {
        "pisa_collection_version": 1,
        "name": name,
        "primitive_count": len(pisa_files),
        "intent_coverage": intent_coverage,
        "themes_included": list(themes.keys()) if themes else [],
        "created_at": datetime.datetime.now().isoformat(),
        "author": author,
    }

    with zipfile.ZipFile(output_path, "w", zipfile.ZIP_DEFLATED) as zf:
        zf.writestr("collection.json", json.dumps(collection_meta, indent=2))
        for pf in pisa_files:
            zf.write(pf, f"primitives/{os.path.basename(pf)}")
        if themes:
            for name, theme_data in themes.items():
                zf.writestr(f"themes/{name}.json", json.dumps(theme_data, indent=2))

    # Cleanup
    import shutil
    shutil.rmtree("/tmp/pisa_export", ignore_errors=True)

    return {"exported": len(pisa_files), "path": output_path}
```

---

## CLI Usage

```bash
# Export single primitive
python3 scripts/library/export_pisa.py --id prim_deck_3_a8f2 --output slide.pisa

# Import single primitive
python3 scripts/library/import_pisa.py slide.pisa --library pisa_library.json

# Export entire library as collection
python3 scripts/library/export_collection.py --library pisa_library.json --output my_library.pisa-collection

# Import collection
python3 scripts/library/import_collection.py my_library.pisa-collection --library pisa_library.json
```
