/**
 * PISA Generator V1 — Template + Theme + Content → PPTX
 * 
 * Usage: node generate.js <config.json> <output.pptx>
 * Config: { slides: [{ template, content, theme }] }
 */
const PptxGenJS = require("pptxgenjs");
const fs = require("fs");

// ═══════════════════════════════════════
// THEME RESOLUTION
// ═══════════════════════════════════════
function resolveColor(token, theme) {
  if (!token) return null;
  if (token.startsWith("token.")) return theme[token] || "333333";
  return token;
}

function getThemeColors(theme) {
  return {
    bg: theme["token.color.background"] || "111827",
    surface: theme["token.color.surface"] || "1f2937",
    text: theme["token.color.text"] || "e5e7eb",
    muted: theme["token.color.text.muted"] || "9ca3af",
    primary: theme["token.color.primary"] || "1A5FB4",
    accent: theme["token.color.accent"] || "F97316",
    secondary: theme["token.color.secondary"] || "0D7377",
    border: theme["token.color.border"] || "374151",
    success: theme["token.color.success"] || "059669",
    warning: theme["token.color.warning"] || "d97706",
    danger: theme["token.color.danger"] || "dc2626",
  };
}

// ═══════════════════════════════════════
// COMPONENT RENDERERS
// ═══════════════════════════════════════
const SLIDE_W = 13.333;
const SLIDE_H = 7.5;

function pct2in(pct, total) { return (pct / 100) * total; }

function addTitle(slide, comp, colors, theme) {
  const x = pct2in(comp.x_pct, SLIDE_W);
  const y = pct2in(comp.y_pct, SLIDE_H);
  const w = pct2in(comp.w_pct, SLIDE_W);
  const h = pct2in(comp.h_pct, SLIDE_H);
  const fontSize = theme["token.size.title"] || 28;
  const vis = comp.visual || {};
  const isDark = vis.bg_variant === "dark" || vis.bg_variant === "accent";

  slide.addText(comp._content || comp.text_preview || "Title", {
    x, y, w, h,
    fontSize,
    fontFace: theme["token.font.heading"] || "Arial",
    color: isDark ? colors.text : colors.primary,
    bold: true,
    valign: "middle",
    align: comp.w_pct > 60 ? "left" : "center",
    margin: [0, 10, 0, 10],
  });

  // Accent bar below title
  slide.addShape("rect", {
    x, y: y + h + 0.05, w: 1.2, h: 0.04,
    fill: { color: colors.accent },
  });
}

function addSubtitle(slide, comp, colors, theme) {
  const x = pct2in(comp.x_pct, SLIDE_W);
  const y = pct2in(comp.y_pct, SLIDE_H);
  const w = pct2in(comp.w_pct, SLIDE_W);
  const h = pct2in(comp.h_pct, SLIDE_H);

  slide.addText(comp._content || comp.text_preview || "Subtitle", {
    x, y, w, h,
    fontSize: theme["token.size.subtitle"] || 18,
    fontFace: theme["token.font.body"] || "Calibri",
    color: colors.muted,
    valign: "middle",
    align: "center",
    margin: [0, 10, 0, 10],
  });
}

function addBody(slide, comp, colors, theme) {
  const x = pct2in(comp.x_pct, SLIDE_W);
  const y = pct2in(comp.y_pct, SLIDE_H);
  const w = pct2in(comp.w_pct, SLIDE_W);
  const h = pct2in(comp.h_pct, SLIDE_H);
  const vis = comp.visual || {};
  const isDark = vis.bg_variant === "dark";
  const bgColor = isDark ? colors.surface : (vis.bg_variant === "accent" ? colors.accent : null);

  // Card background
  if (bgColor) {
    slide.addShape("rect", {
      x, y, w, h,
      fill: { color: bgColor },
      rectRadius: 0.08,
    });
  } else {
    // Light card with border
    slide.addShape("rect", {
      x, y, w, h,
      fill: { color: colors.surface },
      line: { color: colors.border, width: 0.5 },
      rectRadius: 0.08,
    });
  }

  // Left accent border
  if (vis.border === "left") {
    slide.addShape("rect", {
      x, y: y + 0.05, w: 0.04, h: h - 0.1,
      fill: { color: colors.accent },
    });
  }

  // Top accent border
  if (vis.border === "top") {
    slide.addShape("rect", {
      x, y, w, h: 0.04,
      fill: { color: colors.accent },
    });
  }

  const content = comp._content || comp.text_preview || "";
  const textX = vis.border === "left" ? x + 0.15 : x + 0.12;
  const textW = vis.border === "left" ? w - 0.27 : w - 0.24;

  slide.addText(content, {
    x: textX, y: y + 0.1, w: textW, h: h - 0.2,
    fontSize: theme["token.size.body"] || 12,
    fontFace: theme["token.font.body"] || "Calibri",
    color: colors.text,
    valign: "top",
    lineSpacingMultiple: 1.3,
    margin: [5, 5, 5, 5],
  });
}

function addKpiCard(slide, comp, colors, theme) {
  const x = pct2in(comp.x_pct, SLIDE_W);
  const y = pct2in(comp.y_pct, SLIDE_H);
  const w = pct2in(comp.w_pct, SLIDE_W);
  const h = pct2in(comp.h_pct, SLIDE_H);
  const vis = comp.visual || {};
  const kpi = comp.kpi || {};
  const isDark = vis.bg_variant === "dark";
  const bgColor = isDark ? colors.primary : colors.surface;

  // Card background
  slide.addShape("rect", {
    x, y, w, h,
    fill: { color: bgColor },
    line: { color: colors.border, width: 0.5 },
    rectRadius: 0.1,
  });

  // Top accent bar
  slide.addShape("rect", {
    x, y, w, h: 0.05,
    fill: { color: colors.accent },
    rectRadius: 0.1,
  });

  // KPI value
  const value = comp._content_value || kpi.value || comp.text_preview || "—";
  const unit = comp._content_unit || kpi.unit || "";
  const label = comp._content_label || kpi.label || "";
  const annotation = comp._content_annotation || kpi.sub_annotation || "";

  const kpiSize = theme["token.size.kpi"] || 32;
  const valueText = unit && kpi.unit_position === "suffix" ? `${value}${unit}` : value;

  // Value
  slide.addText(valueText, {
    x, y: y + h * 0.12, w, h: h * 0.38,
    fontSize: kpiSize,
    fontFace: theme["token.font.heading"] || "Arial",
    color: isDark ? colors.text : colors.primary,
    bold: true,
    align: "center",
    valign: "middle",
  });

  // Unit (superscript position)
  if (unit && kpi.unit_position === "superscript") {
    slide.addText(unit, {
      x: x + w * 0.6, y: y + h * 0.12, w: w * 0.35, h: h * 0.15,
      fontSize: Math.round(kpiSize * 0.45),
      fontFace: theme["token.font.heading"] || "Arial",
      color: colors.accent,
      align: "left",
      valign: "bottom",
    });
  }

  // Separator line
  if (vis.has_separator) {
    slide.addShape("rect", {
      x: x + w * 0.2, y: y + h * 0.52, w: w * 0.6, h: 0.015,
      fill: { color: colors.muted },
    });
  }

  // Label
  if (label) {
    slide.addText(label, {
      x, y: y + h * 0.56, w, h: h * 0.18,
      fontSize: theme["token.size.label"] || 9,
      fontFace: theme["token.font.body"] || "Calibri",
      color: colors.muted,
      align: "center",
      valign: "middle",
      bold: true,
      charSpacing: 1.5,
    });
  }

  // Sub-annotation
  if (annotation) {
    slide.addText(annotation, {
      x, y: y + h * 0.74, w, h: h * 0.14,
      fontSize: 7,
      fontFace: theme["token.font.body"] || "Calibri",
      color: colors.muted,
      align: "center",
      valign: "middle",
      italic: true,
    });
  }

  // Trend arrow
  if (kpi.trend === "up") {
    slide.addText("▲", {
      x: x + w * 0.82, y: y + h * 0.05, w: w * 0.15, h: h * 0.12,
      fontSize: 10, color: colors.success, align: "center",
    });
  } else if (kpi.trend === "down") {
    slide.addText("▼", {
      x: x + w * 0.82, y: y + h * 0.05, w: w * 0.15, h: h * 0.12,
      fontSize: 10, color: colors.danger, align: "center",
    });
  }
}

function addLabel(slide, comp, colors, theme) {
  const x = pct2in(comp.x_pct, SLIDE_W);
  const y = pct2in(comp.y_pct, SLIDE_H);
  const w = pct2in(comp.w_pct, SLIDE_W);
  const h = pct2in(comp.h_pct, SLIDE_H);

  slide.addText(comp._content || comp.text_preview || "", {
    x, y, w, h,
    fontSize: theme["token.size.label"] || 9,
    fontFace: theme["token.font.body"] || "Calibri",
    color: colors.muted,
    align: "center",
    valign: "middle",
  });
}

function addChart(slide, comp, colors, theme) {
  const x = pct2in(comp.x_pct, SLIDE_W);
  const y = pct2in(comp.y_pct, SLIDE_H);
  const w = pct2in(comp.w_pct, SLIDE_W);
  const h = pct2in(comp.h_pct, SLIDE_H);

  // Chart placeholder with frame
  slide.addShape("rect", {
    x, y, w, h,
    fill: { color: colors.surface },
    line: { color: colors.border, width: 0.5 },
    rectRadius: 0.08,
  });

  // Fake bar chart
  const barCount = 5;
  const barW = (w * 0.7) / barCount;
  const barGap = barW * 0.3;
  const startX = x + w * 0.15;
  const baseY = y + h * 0.85;
  const heights = [0.4, 0.65, 0.5, 0.8, 0.55];

  for (let i = 0; i < barCount; i++) {
    const bh = h * 0.6 * heights[i];
    const isHighlight = i === 3;
    slide.addShape("rect", {
      x: startX + i * (barW + barGap),
      y: baseY - bh,
      w: barW,
      h: bh,
      fill: { color: isHighlight ? colors.accent : colors.primary },
      rectRadius: 0.03,
    });
  }

  // Axis line
  slide.addShape("rect", {
    x: x + w * 0.1, y: baseY, w: w * 0.8, h: 0.01,
    fill: { color: colors.border },
  });

  slide.addText("[Chart — replace with real data]", {
    x, y: y + h * 0.88, w, h: h * 0.1,
    fontSize: 7, color: colors.muted, align: "center",
  });
}

function addTable(slide, comp, colors, theme) {
  const x = pct2in(comp.x_pct, SLIDE_W);
  const y = pct2in(comp.y_pct, SLIDE_H);
  const w = pct2in(comp.w_pct, SLIDE_W);
  const h = pct2in(comp.h_pct, SLIDE_H);

  // Table placeholder
  const rows = comp._content_rows || [
    ["Header 1", "Header 2", "Header 3", "Header 4"],
    ["Row 1", "Data", "Data", "Data"],
    ["Row 2", "Data", "Data", "Data"],
    ["Row 3", "Data", "Data", "Data"],
  ];

  const tableRows = rows.map((row, ri) =>
    row.map(cell => ({
      text: String(cell),
      options: {
        fontSize: ri === 0 ? 10 : 9,
        fontFace: theme["token.font.body"] || "Calibri",
        color: ri === 0 ? colors.text : colors.text,
        bold: ri === 0,
        fill: { color: ri === 0 ? colors.primary : (ri % 2 === 0 ? colors.surface : colors.bg) },
        border: { type: "solid", color: colors.border, pt: 0.5 },
        valign: "middle",
        margin: [3, 5, 3, 5],
      },
    }))
  );

  slide.addTable(tableRows, {
    x, y, w,
    rowH: Math.min(h / rows.length, 0.45),
    colW: Array(rows[0].length).fill(w / rows[0].length),
  });
}

function addImage(slide, comp, colors, theme) {
  const x = pct2in(comp.x_pct, SLIDE_W);
  const y = pct2in(comp.y_pct, SLIDE_H);
  const w = pct2in(comp.w_pct, SLIDE_W);
  const h = pct2in(comp.h_pct, SLIDE_H);

  // Image placeholder
  slide.addShape("rect", {
    x, y, w, h,
    fill: { color: colors.surface },
    line: { color: colors.border, width: 0.5 },
    rectRadius: 0.08,
  });

  slide.addText("[Image]", {
    x, y, w, h,
    fontSize: 12, color: colors.muted, align: "center", valign: "middle",
  });
}

function addFooter(slide, comp, colors, theme) {
  const x = pct2in(comp.x_pct, SLIDE_W);
  const y = pct2in(comp.y_pct, SLIDE_H);
  const w = pct2in(comp.w_pct, SLIDE_W);
  const h = pct2in(comp.h_pct, SLIDE_H);

  slide.addText(comp._content || comp.text_preview || "", {
    x, y, w, h,
    fontSize: 7,
    fontFace: theme["token.font.body"] || "Calibri",
    color: colors.muted,
    align: "right",
    valign: "bottom",
  });
}

// ═══════════════════════════════════════
// MAIN GENERATOR
// ═══════════════════════════════════════
const RENDERERS = {
  title: addTitle,
  subtitle: addSubtitle,
  body: addBody,
  kpi_card: addKpiCard,
  label: addLabel,
  chart: addChart,
  table: addTable,
  image: addImage,
  footer: addFooter,
  shape: addBody,      // fallback
  decoration: () => {}, // skip
};

function renderSlide(pptx, template, theme, content) {
  const colors = getThemeColors(theme);
  const slide = pptx.addSlide();

  // Slide background
  slide.background = { fill: colors.bg };

  // Top accent bar
  slide.addShape("rect", {
    x: 0, y: 0, w: SLIDE_W, h: 0.04,
    fill: { color: colors.accent },
  });

  // Render components in reading order
  const order = template.reading_order || template.components.map((_, i) => i);

  for (const idx of order) {
    const comp = template.components[idx];
    if (!comp) continue;

    // Merge content overrides
    if (content && content[idx]) {
      const override = content[idx];
      if (typeof override === "string") {
        comp._content = override;
      } else if (typeof override === "object") {
        comp._content = override.text || comp.text_preview;
        comp._content_value = override.value;
        comp._content_unit = override.unit;
        comp._content_label = override.label;
        comp._content_annotation = override.annotation;
        comp._content_rows = override.rows;
      }
    }

    const renderer = RENDERERS[comp.role] || addBody;
    renderer(slide, comp, colors, theme);
  }

  // Slide number
  slide.addText("{{slideNumber}}", {
    x: SLIDE_W - 0.7, y: SLIDE_H - 0.3, w: 0.5, h: 0.2,
    fontSize: 7, color: colors.muted, align: "right",
  });

  return slide;
}

// ═══════════════════════════════════════
// CLI
// ═══════════════════════════════════════
if (require.main === module) {
  const configPath = process.argv[2] || "deck_config.json";
  const outputPath = process.argv[3] || "output.pptx";

  const config = JSON.parse(fs.readFileSync(configPath, "utf8"));
  const pptx = new PptxGenJS();
  pptx.layout = "LAYOUT_WIDE";
  pptx.author = "PISA Generator";

  for (const slideConf of config.slides) {
    renderSlide(pptx, slideConf.template, slideConf.theme, slideConf.content);
  }

  pptx.writeFile({ fileName: outputPath }).then(() => {
    console.log(`✅ Generated: ${outputPath} (${config.slides.length} slides)`);
  });
}

module.exports = { renderSlide, getThemeColors };
