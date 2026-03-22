"""
PISA SVG Renderer V2.1 — Supports kpi{}, visual{}, content_data{}.
Zero dependencies. Pure string generation.
"""
import html, json, math

NEUTRAL_THEME = {
    "token.color.primary":"1a1a2e","token.color.secondary":"16213e",
    "token.color.accent":"e94560","token.color.background":"f5f5f5",
    "token.color.text":"1a1a2e","token.color.text.muted":"6b7280",
    "token.color.border":"d1d5db","token.color.surface":"ffffff",
    "token.color.success":"059669","token.color.warning":"d97706",
    "token.color.danger":"dc2626",
    "token.font.heading":"system-ui, sans-serif","token.font.body":"system-ui, sans-serif",
}

def _t(theme, key, fallback=None):
    return theme.get(key, NEUTRAL_THEME.get(key, fallback or "888888"))

def _vis(comp):
    return comp.get("visual", {})

def _bg_colors(comp, theme):
    vis = _vis(comp)
    bv = vis.get("bg_variant", "light")
    primary = _t(theme, "token.color.primary")
    surface = _t(theme, "token.color.surface", "ffffff")
    accent = _t(theme, "token.color.accent")
    if bv == "dark": return primary, surface, accent
    if bv == "accent": return accent, surface, surface
    return surface, _t(theme, "token.color.text"), _t(theme, "token.color.text.muted")

# ═══════════════════════════════════════════════════
# COMPONENT RENDERERS
# ═══════════════════════════════════════════════════

def _render_title(x, y, w, h, comp, theme, W, H):
    bg, fg, muted = _bg_colors(comp, theme)
    accent = _t(theme, "token.color.accent")
    font = _t(theme, "token.font.heading")
    text = html.escape(comp.get("text_preview", "Slide Title")[:60])
    fs = min(h * 0.55, w * 0.035)
    return (
        f'<rect x="{x:.1f}" y="{y:.1f}" width="{w:.1f}" height="{h:.1f}" fill="#{bg}" rx="4"/>'
        f'<text x="{x+w/2:.1f}" y="{y+h*0.55:.1f}" text-anchor="middle" dominant-baseline="central" '
        f'font-family="{font}" font-size="{fs:.1f}" font-weight="bold" fill="#{fg}">{text}</text>'
        f'<rect x="{x:.1f}" y="{y+h-2:.1f}" width="{min(w*0.35,120):.1f}" height="2.5" fill="#{accent}" rx="1"/>'
    )

def _render_subtitle(x, y, w, h, comp, theme, W, H):
    bg, fg, _ = _bg_colors(comp, theme)
    font = _t(theme, "token.font.heading")
    text = html.escape(comp.get("text_preview", "Subtitle")[:40])
    fs = min(h * 0.5, w * 0.025)
    return (
        f'<rect x="{x:.1f}" y="{y:.1f}" width="{w:.1f}" height="{h:.1f}" fill="#{bg}" rx="3" opacity="0.85"/>'
        f'<text x="{x+w/2:.1f}" y="{y+h*0.55:.1f}" text-anchor="middle" dominant-baseline="central" '
        f'font-family="{font}" font-size="{fs:.1f}" fill="#{fg}">{text}</text>'
    )

def _render_body(x, y, w, h, comp, theme, W, H):
    bg, fg, muted = _bg_colors(comp, theme)
    border = _t(theme, "token.color.border")
    accent = _t(theme, "token.color.accent")
    vis = _vis(comp)
    bdr = vis.get("border", "left")

    parts = [f'<rect x="{x:.1f}" y="{y:.1f}" width="{w:.1f}" height="{h:.1f}" fill="#{bg}" stroke="#{border}" stroke-width="0.8" rx="5"/>']

    if bdr == "left":
        parts.append(f'<rect x="{x:.1f}" y="{y+4:.1f}" width="3" height="{h-8:.1f}" fill="#{accent}" rx="1.5" opacity="0.6"/>')
    elif bdr == "top":
        parts.append(f'<rect x="{x+4:.1f}" y="{y:.1f}" width="{w-8:.1f}" height="3" fill="#{accent}" rx="1.5" opacity="0.6"/>')

    # V2.1: Structured content_data
    cd = comp.get("content_data")
    if cd and cd.get("entries"):
        entries = cd["entries"][:6]
        ey = y + h * 0.08
        efs = min(8, w * 0.025)
        for entry in entries:
            key = html.escape(str(entry.get("key", ""))[:12])
            txt = html.escape(str(entry.get("text", ""))[:40])
            parts.append(f'<text x="{x+12:.1f}" y="{ey+efs:.1f}" font-family="{_t(theme,"token.font.body")}" '
                         f'font-size="{efs:.1f}" font-weight="bold" fill="#{fg}">{key}</text>')
            parts.append(f'<text x="{x+12+len(key)*efs*0.6:.1f}" y="{ey+efs:.1f}" font-family="{_t(theme,"token.font.body")}" '
                         f'font-size="{efs*0.85:.1f}" fill="#{muted}"> {txt}</text>')
            ey += efs * 1.8
    else:
        # Text preview lines
        preview = comp.get("text_preview", "")
        line_h = max(8, min(14, h / 8))
        mx = max(12, w * 0.06)
        mt = max(8, h * 0.1)
        max_lines = min(int((h - mt*2) / line_h), 7)
        if preview:
            words = preview.split()
            ly = y + mt + line_h * 0.7
            fs = min(line_h * 0.8, w * 0.025)
            cpl = int(w / (fs * 0.52))
            line, lc = "", 0
            for word in words:
                if len(line) + len(word) + 1 > cpl:
                    if line and lc < max_lines:
                        parts.append(f'<text x="{x+mx:.1f}" y="{ly:.1f}" font-family="{_t(theme,"token.font.body")}" font-size="{fs:.1f}" fill="#{fg}">{html.escape(line)}</text>')
                        ly += line_h; lc += 1
                    line = word
                else:
                    line = f"{line} {word}".strip()
            if line and lc < max_lines:
                parts.append(f'<text x="{x+mx:.1f}" y="{ly:.1f}" font-family="{_t(theme,"token.font.body")}" font-size="{fs:.1f}" fill="#{fg}">{html.escape(line)}</text>')
        else:
            for i in range(min(max_lines, 5)):
                ly = y + mt + i * line_h
                lw = (w - mx*2) * (0.6 if i >= 4 else 1)
                parts.append(f'<rect x="{x+mx:.1f}" y="{ly:.1f}" width="{lw:.1f}" height="{line_h*0.35:.1f}" fill="#{muted}" rx="1.5" opacity="0.18"/>')
    return "\n".join(parts)

def _render_kpi_card(x, y, w, h, comp, theme, W, H):
    accent = _t(theme, "token.color.accent")
    font = _t(theme, "token.font.heading")
    bg, fg, muted = _bg_colors(comp, theme)
    vis = _vis(comp)
    has_sep = vis.get("has_separator", True)
    has_icon = vis.get("has_icon", False)
    icon_hint = vis.get("icon_hint", "")

    kpi = comp.get("kpi", {})
    value = kpi.get("value", comp.get("text_preview", "—")[:12])
    unit = kpi.get("unit", "")
    label = kpi.get("label", "")
    sub_ann = kpi.get("sub_annotation", "")
    trend = kpi.get("trend")

    fs = min(h * 0.30, w * 0.20)
    seed = sum(ord(c) for c in value) % 7

    parts = [
        f'<rect x="{x:.1f}" y="{y:.1f}" width="{w:.1f}" height="{h:.1f}" fill="#{bg}" stroke="#{_t(theme,"token.color.border")}" stroke-width="0.8" rx="6"/>',
        f'<rect x="{x:.1f}" y="{y:.1f}" width="{w:.1f}" height="3.5" fill="#{accent}" rx="6"/>',
        f'<rect x="{x:.1f}" y="{y+1.5:.1f}" width="{w:.1f}" height="2" fill="#{accent}"/>',
    ]

    if has_icon and icon_hint:
        ir = min(w, h) * 0.07
        parts.append(f'<circle cx="{x+w*0.78:.1f}" cy="{y+h*0.15:.1f}" r="{ir:.1f}" fill="#{accent}" opacity="0.12"/>')
        parts.append(f'<text x="{x+w*0.78:.1f}" y="{y+h*0.15+2:.1f}" text-anchor="middle" font-size="5" fill="#{muted}" opacity="0.4">{html.escape(icon_hint[:6])}</text>')

    val_y = y + h * 0.30 if label else y + h * 0.42
    parts.append(f'<text x="{x+w/2:.1f}" y="{val_y:.1f}" text-anchor="middle" dominant-baseline="central" '
                 f'font-family="{font}" font-size="{fs:.1f}" font-weight="bold" fill="#{fg}">{html.escape(value)}</text>')
    if unit:
        ufs = fs * 0.38
        parts.append(f'<text x="{x+w/2+len(value)*fs*0.3:.1f}" y="{val_y-fs*0.18:.1f}" text-anchor="start" '
                     f'font-family="{font}" font-size="{ufs:.1f}" fill="#{fg}" opacity="0.75">{html.escape(unit)}</text>')
    if has_sep:
        sy = val_y + fs * 0.45
        parts.append(f'<rect x="{x+w*0.25:.1f}" y="{sy:.1f}" width="{w*0.5:.1f}" height="1.5" fill="#{muted}" rx="0.75" opacity="0.25"/>')
    if label:
        ly = val_y + fs * 0.7
        lfs = min(7.5, w * 0.022)
        parts.append(f'<text x="{x+w/2:.1f}" y="{ly:.1f}" text-anchor="middle" font-family="{font}" '
                     f'font-size="{lfs:.1f}" fill="#{muted}" letter-spacing="1.5">{html.escape(label[:28])}</text>')
    if sub_ann:
        parts.append(f'<text x="{x+w/2:.1f}" y="{y+h*0.90:.1f}" text-anchor="middle" font-size="5.5" fill="#{muted}" '
                     f'font-style="italic" opacity="0.5">{html.escape(sub_ann[:25])}</text>')

    # Sparkline
    sk_y, sk_h, sk_w = y+h*0.72 if label else y+h*0.62, h*0.10, w*0.45
    sk_x = x+(w-sk_w)/2
    pr = [(seed+1)*0.3,(seed+2)*0.5,seed*0.4,(seed+3)*0.6,(seed+1)*0.7,(seed+2)*0.5,(seed+4)*0.8]
    pmx,pmn = max(pr),min(pr); rng = pmx-pmn if pmx!=pmn else 1
    pts = " ".join(f"{sk_x+i/(len(pr)-1)*sk_w:.1f},{sk_y+sk_h-((v-pmn)/rng)*sk_h:.1f}" for i,v in enumerate(pr))
    parts.append(f'<polyline points="{pts}" fill="none" stroke="#{accent}" stroke-width="1" stroke-linecap="round" opacity="0.3"/>')

    if trend in ("up","down"):
        ax,ay = x+w*0.87, sk_y+sk_h*0.5
        ac = _t(theme,"token.color.success") if trend=="up" else _t(theme,"token.color.danger")
        d = f"M{ax:.0f},{ay+4:.0f}L{ax:.0f},{ay-2:.0f}L{ax-3:.0f},{ay+1:.0f}M{ax:.0f},{ay-2:.0f}L{ax+3:.0f},{ay+1:.0f}" if trend=="up" else f"M{ax:.0f},{ay-2:.0f}L{ax:.0f},{ay+4:.0f}L{ax-3:.0f},{ay+1:.0f}M{ax:.0f},{ay+4:.0f}L{ax+3:.0f},{ay+1:.0f}"
        parts.append(f'<path d="{d}" stroke="#{ac}" stroke-width="1.5" fill="none" stroke-linecap="round"/>')

    return "\n".join(parts)

def _render_chart(x, y, w, h, comp, theme, W, H):
    bg, fg, muted = _bg_colors(comp, theme)
    border = _t(theme, "token.color.border")
    accent = _t(theme, "token.color.accent")
    primary = _t(theme, "token.color.primary")
    parts = [f'<rect x="{x:.1f}" y="{y:.1f}" width="{w:.1f}" height="{h:.1f}" fill="#{bg}" stroke="#{border}" stroke-width="0.8" rx="5"/>']
    cx, cy, cw, ch = x+w*0.12, y+h*0.12, w*0.76, h*0.72
    bars = [0.45, 0.72, 0.58, 0.88, 0.65, 0.78, 0.92]
    bw = cw / (len(bars)*1.6); gap = bw*0.6
    axis_y = cy + ch
    parts.append(f'<line x1="{cx:.1f}" y1="{axis_y:.1f}" x2="{cx+cw:.1f}" y2="{axis_y:.1f}" stroke="#{border}" stroke-width="0.7"/>')
    for i in range(1,4):
        gy = cy+ch*(1-i/4)
        parts.append(f'<line x1="{cx:.1f}" y1="{gy:.1f}" x2="{cx+cw:.1f}" y2="{gy:.1f}" stroke="#{border}" stroke-width="0.3" stroke-dasharray="3,3"/>')
    colors = [primary, primary, primary, accent, primary, primary, accent]
    for i, val in enumerate(bars):
        bx = cx + i*(bw+gap)+gap/2; bh = ch*val*0.9; by = axis_y-bh
        parts.append(f'<rect x="{bx:.1f}" y="{by:.1f}" width="{bw:.1f}" height="{bh:.1f}" fill="#{colors[i%len(colors)]}" rx="2" opacity="0.8"/>')
    parts.append(f'<text x="{x+w/2:.1f}" y="{y+h-4:.1f}" text-anchor="middle" font-family="monospace" font-size="7" fill="#{muted}" opacity="0.4">chart</text>')
    return "\n".join(parts)

def _render_table(x, y, w, h, comp, theme, W, H):
    border = _t(theme, "token.color.border")
    bg, fg, muted = _bg_colors(comp, theme)
    primary = _t(theme, "token.color.primary")
    bgc = _t(theme, "token.color.background")
    size = comp.get("table_size", "5x4")
    try: cols, rows = [int(v) for v in size.split("x")]
    except: cols, rows = 5, 4
    rows, cols = min(rows,8), min(cols,7)
    parts = [f'<rect x="{x:.1f}" y="{y:.1f}" width="{w:.1f}" height="{h:.1f}" fill="#{bg}" stroke="#{border}" stroke-width="0.8" rx="4"/>']
    rh = h/(rows+1); cw2 = (w-4)/cols
    parts.append(f'<rect x="{x+1:.1f}" y="{y+1:.1f}" width="{w-2:.1f}" height="{rh:.1f}" fill="#{primary}" rx="3" opacity="0.9"/>')
    for c in range(cols):
        cx2 = x+2+c*cw2+cw2/2
        parts.append(f'<rect x="{cx2-cw2*0.3:.1f}" y="{y+rh*0.35:.1f}" width="{cw2*0.6:.1f}" height="{rh*0.3:.1f}" fill="#{_t(theme,"token.color.surface")}" rx="1.5" opacity="0.4"/>')
    for r in range(rows):
        ry = y+(r+1)*rh+1
        if r%2==1:
            parts.append(f'<rect x="{x+1:.1f}" y="{ry:.1f}" width="{w-2:.1f}" height="{rh:.1f}" fill="#{bgc}" opacity="0.5"/>')
        parts.append(f'<line x1="{x+2:.1f}" y1="{ry+rh:.1f}" x2="{x+w-2:.1f}" y2="{ry+rh:.1f}" stroke="#{border}" stroke-width="0.3" opacity="0.25"/>')
        for c in range(cols):
            cx2 = x+2+c*cw2+cw2/2
            pw = cw2*(0.5+(hash(f"{r}{c}")%3)*0.1)
            parts.append(f'<rect x="{cx2-pw/2:.1f}" y="{ry+rh*0.3:.1f}" width="{pw:.1f}" height="{rh*0.3:.1f}" fill="#{muted}" rx="1.5" opacity="0.12"/>')
    return "\n".join(parts)

def _render_image(x, y, w, h, comp, theme, W, H):
    border = _t(theme, "token.color.border")
    bgc = _t(theme, "token.color.background")
    muted = _t(theme, "token.color.text.muted")
    accent = _t(theme, "token.color.accent")
    vis = _vis(comp)
    hint = vis.get("image_bg_hint", "") if vis.get("has_image_bg") else ""
    parts = [f'<rect x="{x:.1f}" y="{y:.1f}" width="{w:.1f}" height="{h:.1f}" fill="#{bgc}" stroke="#{border}" stroke-width="0.8" rx="5"/>']
    sun_cx, sun_cy, sun_r = x+w*0.75, y+h*0.28, min(w,h)*0.08
    parts.append(f'<circle cx="{sun_cx:.1f}" cy="{sun_cy:.1f}" r="{sun_r:.1f}" fill="#{accent}" opacity="0.25"/>')
    m1 = f"{x+w*0.05:.0f},{y+h*0.85:.0f} {x+w*0.25:.0f},{y+h*0.35:.0f} {x+w*0.5:.0f},{y+h*0.85:.0f}"
    m2 = f"{x+w*0.35:.0f},{y+h*0.85:.0f} {x+w*0.6:.0f},{y+h*0.45:.0f} {x+w*0.85:.0f},{y+h*0.85:.0f}"
    parts.append(f'<polygon points="{m1}" fill="#{muted}" opacity="0.15"/>')
    parts.append(f'<polygon points="{m2}" fill="#{muted}" opacity="0.1"/>')
    lbl = hint[:15] if hint else "image"
    parts.append(f'<text x="{x+w/2:.1f}" y="{y+h*0.92:.1f}" text-anchor="middle" font-family="monospace" font-size="7" fill="#{muted}" opacity="0.3">{html.escape(lbl)}</text>')
    return "\n".join(parts)

def _render_label(x, y, w, h, comp, theme, W, H):
    text = html.escape(comp.get("text_preview", "Label")[:25])
    _, fg, muted = _bg_colors(comp, theme)
    font = _t(theme, "token.font.body")
    fs = min(h * 0.6, w * 0.04, 11)
    return f'<text x="{x+w/2:.1f}" y="{y+h*0.6:.1f}" text-anchor="middle" dominant-baseline="central" font-family="{font}" font-size="{fs:.1f}" fill="#{muted}" opacity="0.7">{text}</text>'

def _render_footer(x, y, w, h, comp, theme, W, H):
    text = html.escape(comp.get("text_preview", "")[:30])
    muted = _t(theme, "token.color.text.muted")
    border = _t(theme, "token.color.border")
    parts = [f'<line x1="{x:.1f}" y1="{y:.1f}" x2="{x+w:.1f}" y2="{y:.1f}" stroke="#{border}" stroke-width="0.5" opacity="0.3"/>']
    if text:
        parts.append(f'<text x="{x+w/2:.1f}" y="{y+h*0.6:.1f}" text-anchor="middle" font-family="{_t(theme,"token.font.body")}" font-size="7" fill="#{muted}" opacity="0.5">{text}</text>')
    return "\n".join(parts)

_RENDERERS = {
    "title": _render_title, "subtitle": _render_subtitle, "body": _render_body,
    "kpi_card": _render_kpi_card, "chart": _render_chart, "table": _render_table,
    "image": _render_image, "label": _render_label, "footer": _render_footer,
}

# ═══════════════════════════════════════════════════
# MAIN RENDERER
# ═══════════════════════════════════════════════════

def render_svg(template, theme=None, width=960, height=540, show_labels=True, show_groups=True):
    if theme is None: theme = NEUTRAL_THEME
    components = template.get("components", [])
    groups = template.get("semantic_groups", [])
    intent = template.get("intent", "unknown")
    layout = template.get("layout_type", "")
    lv = template.get("layout_variant", "")
    quality = template.get("quality_score", 0)
    accent = _t(theme, "token.color.accent")
    bg = _t(theme, "token.color.background")
    border = _t(theme, "token.color.border")
    muted = _t(theme, "token.color.text.muted")

    parts = []
    parts.append(f'<rect width="{width}" height="{height}" fill="#{bg}" rx="6"/>')
    parts.append(f'<rect x="0.5" y="0.5" width="{width-1}" height="{height-1}" fill="none" stroke="#{border}" stroke-width="1" rx="6"/>')
    parts.append(f'<rect x="0" y="0" width="{width}" height="3" fill="#{accent}" rx="6"/>')
    parts.append(f'<rect x="0" y="1.5" width="{width}" height="1.5" fill="#{accent}"/>')

    if show_groups:
        for group in groups:
            if group.get("type") == "standalone": continue
            members = [m for m in group.get("members", []) if m < len(components)]
            if len(members) < 2: continue
            min_x = min(components[m]["x_pct"] for m in members)
            min_y = min(components[m]["y_pct"] for m in members)
            max_x = max(components[m]["x_pct"]+components[m]["w_pct"] for m in members)
            max_y = max(components[m]["y_pct"]+components[m]["h_pct"] for m in members)
            gx,gy = (min_x/100)*width-4, (min_y/100)*height-4
            gw,gh = ((max_x-min_x)/100)*width+8, ((max_y-min_y)/100)*height+8
            parts.append(f'<rect x="{gx:.1f}" y="{gy:.1f}" width="{gw:.1f}" height="{gh:.1f}" fill="none" stroke="#{accent}" stroke-width="1.2" stroke-dasharray="5,3" rx="8" opacity="0.3"/>')

    # Render zones if present (V2.1)
    zones = template.get("zones", [])
    for zone in zones:
        zx = (zone["x_pct"]/100)*width; zy = (zone["y_pct"]/100)*height
        zw = (zone["w_pct"]/100)*width; zh = (zone["h_pct"]/100)*height
        parts.append(f'<rect x="{zx:.1f}" y="{zy:.1f}" width="{zw:.1f}" height="{zh:.1f}" fill="none" stroke="#{muted}" stroke-width="0.8" stroke-dasharray="8,4" rx="4" opacity="0.2"/>')
        zi = zone.get("zone_intent", "")
        if zi:
            parts.append(f'<text x="{zx+4:.1f}" y="{zy+10:.1f}" font-family="monospace" font-size="6" fill="#{muted}" opacity="0.25">{zi}</text>')

    for i, comp in enumerate(components):
        role = comp.get("role", "body")
        if role == "decoration": continue
        cx = (comp["x_pct"]/100)*width; cy = (comp["y_pct"]/100)*height
        cw = (comp["w_pct"]/100)*width; ch = (comp["h_pct"]/100)*height
        renderer = _RENDERERS.get(role, _render_body)
        parts.append(renderer(cx, cy, cw, ch, comp, theme, width, height))
        if show_labels and role not in ("decoration", "label", "footer"):
            parts.append(f'<text x="{cx+3:.1f}" y="{cy+8:.1f}" font-family="monospace" font-size="6" fill="#{muted}" opacity="0.35">{role}</text>')

    lv_str = f" · {lv}" if lv else ""
    parts.append(f'<text x="{width-8:.0f}" y="{height-6:.0f}" text-anchor="end" font-family="monospace" font-size="7.5" fill="#{muted}" opacity="0.45">{intent} · {layout}{lv_str} · Q:{quality}</text>')
    return f'<svg viewBox="0 0 {width} {height}" xmlns="http://www.w3.org/2000/svg">\n' + "\n".join(parts) + '\n</svg>'

def render_svg_grid(templates, theme=None, columns=3, cell_w=320, cell_h=180, gap=12):
    if theme is None: theme = NEUTRAL_THEME
    n = len(templates); rows = math.ceil(n / columns)
    tw = columns*cell_w+(columns-1)*gap; th = rows*(cell_h+22)+(rows-1)*gap
    parts = [f'<svg viewBox="0 0 {tw} {th}" xmlns="http://www.w3.org/2000/svg">']
    for i, prim in enumerate(templates):
        col, row = i%columns, i//columns
        ox = col*(cell_w+gap); oy = row*(cell_h+22+gap)
        inner = render_svg(prim, theme, cell_w, cell_h, False, False)
        content = inner.split(">",1)[1].rsplit("</svg>",1)[0]
        parts.append(f'<g transform="translate({ox},{oy})">{content}</g>')
        label = f'{prim.get("intent","?")} (Q:{prim.get("quality_score",0)})'
        parts.append(f'<text x="{ox+cell_w/2:.0f}" y="{oy+cell_h+14:.0f}" text-anchor="middle" font-family="monospace" font-size="9" fill="#6b7280">{label}</text>')
    parts.append('</svg>')
    return "\n".join(parts)

def render_svg_theme_compare(template, themes_dict, cell_w=440, cell_h=250, gap=20):
    n = len(themes_dict); tw = n*cell_w+(n-1)*gap; th = cell_h+24
    parts = [f'<svg viewBox="0 0 {tw} {th}" xmlns="http://www.w3.org/2000/svg">']
    for i, (name, theme) in enumerate(themes_dict.items()):
        ox = i*(cell_w+gap)
        inner = render_svg(template, theme, cell_w, cell_h, False, False)
        content = inner.split(">",1)[1].rsplit("</svg>",1)[0]
        parts.append(f'<g transform="translate({ox},0)">{content}</g>')
        parts.append(f'<text x="{ox+cell_w/2:.0f}" y="{cell_h+16:.0f}" text-anchor="middle" font-family="monospace" font-size="10" fill="#6b7280">{html.escape(name)}</text>')
    parts.append('</svg>')
    return "\n".join(parts)

def generate_pack_svgs(pack, theme_name=None):
    themes = pack.get("themes", {})
    theme = themes.get(theme_name, list(themes.values())[0] if themes else NEUTRAL_THEME)
    for prim in pack.get("templates", []):
        prim["svg"] = render_svg(prim, theme, 960, 540, show_labels=False, show_groups=True)
    return pack

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="PISA SVG Renderer V2.1")
    parser.add_argument("--template", help="Path to template JSON")
    parser.add_argument("--theme", help="Path to theme JSON")
    parser.add_argument("--output", default="output.svg")
    args = parser.parse_args()
    if args.template:
        with open(args.template) as f: prim = json.load(f)
        theme = json.load(open(args.theme)) if args.theme else None
        svg = render_svg(prim, theme)
        with open(args.output, "w") as f: f.write(svg)
        print(f"OK {args.output}")
