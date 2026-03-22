# PISA Template Versioning & Diff

## Purpose

Track template evolution over time. When a deck is re-extracted after modifications,
PISA creates a new version instead of a blind overwrite. The diff tool shows exactly
what changed between versions.

---

## Version Model

Every template has:
- `version` (integer, starting at 1)
- `_content_hash` (SHA-256 of components JSON, first 12 chars)
- `previous_hash` (hash of the version it replaced, if any)
- `source.extracted_at` (timestamp)

Same-source detection: if a newly extracted template has the same `source.file` +
`source.slide` as an existing library entry, PISA increments the version and stores
the `previous_hash` link. The old version is replaced in the active library but can
be recovered from the version log.

## Version Log

Maintained alongside the library. Records every version transition.

```json
// pisa_version_log.json
{
  "log_version": 1,
  "entries": [
    {
      "template_id": "prim_quarterly_3_a8f2c1d9e4b7",
      "from_version": 1,
      "to_version": 2,
      "from_hash": "a8f2c1d9e4b7",
      "to_hash": "b3c7d8e9f1a2",
      "timestamp": "2026-03-21T14:30:00Z",
      "changes_summary": {
        "components_added": 1,
        "components_removed": 0,
        "components_moved": 2,
        "roles_changed": 1,
        "intent_changed": false,
        "quality_delta": +0.5
      }
    }
  ]
}
```

## Diff Algorithm

```python
import json

def diff_templates(prim_a, prim_b):
    """Compare two template versions. Returns structured diff report."""
    diff = {
        "id": prim_b.get("id", prim_a.get("id")),
        "version_a": prim_a.get("version", 1),
        "version_b": prim_b.get("version", 2),
        "hash_a": prim_a.get("_content_hash"),
        "hash_b": prim_b.get("_content_hash"),
        "changes": [],
    }

    # Intent change
    if prim_a["intent"] != prim_b["intent"]:
        diff["changes"].append({
            "type": "intent_changed",
            "from": prim_a["intent"],
            "to": prim_b["intent"],
            "severity": "major"
        })

    # Layout type change
    if prim_a.get("layout_type") != prim_b.get("layout_type"):
        diff["changes"].append({
            "type": "layout_changed",
            "from": prim_a.get("layout_type"),
            "to": prim_b.get("layout_type"),
            "severity": "major"
        })

    # Component diff (by role matching, then position delta)
    ca = prim_a.get("components", [])
    cb = prim_b.get("components", [])

    if len(ca) != len(cb):
        diff["changes"].append({
            "type": "component_count_changed",
            "from": len(ca), "to": len(cb),
            "severity": "moderate"
        })

    # Match components by role + proximity
    matched = _match_components(ca, cb)
    for match in matched:
        if match["type"] == "moved":
            diff["changes"].append({
                "type": "component_moved",
                "role": match["role"],
                "dx_pct": match["dx"], "dy_pct": match["dy"],
                "severity": "minor" if abs(match["dx"]) < 5 and abs(match["dy"]) < 5 else "moderate"
            })
        elif match["type"] == "resized":
            diff["changes"].append({
                "type": "component_resized",
                "role": match["role"],
                "dw_pct": match["dw"], "dh_pct": match["dh"],
                "severity": "minor"
            })
        elif match["type"] == "role_changed":
            diff["changes"].append({
                "type": "role_changed",
                "from_role": match["from_role"], "to_role": match["to_role"],
                "severity": "moderate"
            })
        elif match["type"] == "added":
            diff["changes"].append({
                "type": "component_added",
                "role": match["role"],
                "position": f"({match['x']:.1f}%, {match['y']:.1f}%)",
                "severity": "moderate"
            })
        elif match["type"] == "removed":
            diff["changes"].append({
                "type": "component_removed",
                "role": match["role"],
                "severity": "moderate"
            })

    # Quality delta
    qa = prim_a.get("quality_score", 0)
    qb = prim_b.get("quality_score", 0)
    if qa != qb:
        diff["changes"].append({
            "type": "quality_changed",
            "from": qa, "to": qb, "delta": round(qb - qa, 1),
            "severity": "info"
        })

    # Token changes
    ta = set(prim_a.get("design_tokens", {}).get("colors", {}).values())
    tb = set(prim_b.get("design_tokens", {}).get("colors", {}).values())
    added_tokens = tb - ta
    removed_tokens = ta - tb
    if added_tokens or removed_tokens:
        diff["changes"].append({
            "type": "tokens_changed",
            "added": list(added_tokens),
            "removed": list(removed_tokens),
            "severity": "minor"
        })

    diff["summary"] = {
        "total_changes": len(diff["changes"]),
        "major": sum(1 for c in diff["changes"] if c["severity"] == "major"),
        "moderate": sum(1 for c in diff["changes"] if c["severity"] == "moderate"),
        "minor": sum(1 for c in diff["changes"] if c["severity"] == "minor"),
    }

    return diff


def _match_components(ca, cb):
    """Match components between two versions using role + position proximity."""
    results = []
    used_b = set()

    for a in ca:
        best_j, best_d = -1, 999
        for j, b in enumerate(cb):
            if j in used_b:
                continue
            # Same role gets priority
            role_bonus = 0 if a.get("role") == b.get("role") else 20
            d = (abs(a["x_pct"]-b["x_pct"]) + abs(a["y_pct"]-b["y_pct"]) +
                 abs(a["w_pct"]-b["w_pct"]) + abs(a["h_pct"]-b["h_pct"]))/4 + role_bonus
            if d < best_d:
                best_d, best_j = d, j

        if best_j >= 0 and best_d < 30:
            b = cb[best_j]
            used_b.add(best_j)
            dx = b["x_pct"] - a["x_pct"]
            dy = b["y_pct"] - a["y_pct"]
            dw = b["w_pct"] - a["w_pct"]
            dh = b["h_pct"] - a["h_pct"]
            if a.get("role") != b.get("role"):
                results.append({"type": "role_changed", "from_role": a.get("role"),
                                "to_role": b.get("role")})
            elif abs(dx) > 1.5 or abs(dy) > 1.5:
                results.append({"type": "moved", "role": a.get("role"), "dx": round(dx,1), "dy": round(dy,1)})
            elif abs(dw) > 2 or abs(dh) > 2:
                results.append({"type": "resized", "role": a.get("role"), "dw": round(dw,1), "dh": round(dh,1)})
        else:
            results.append({"type": "removed", "role": a.get("role")})

    for j, b in enumerate(cb):
        if j not in used_b:
            results.append({"type": "added", "role": b.get("role"),
                            "x": b["x_pct"], "y": b["y_pct"]})

    return results
```

## CLI Usage

```bash
# Show diff between two versions (by template ID)
python3 scripts/library/diff.py --id prim_deck_3_a8f2 --v1 1 --v2 2

# Show version history for a template
python3 scripts/library/diff.py --id prim_deck_3_a8f2 --history

# Compare two .pisa files directly
python3 scripts/library/diff.py --file-a old.pisa --file-b new.pisa
```
