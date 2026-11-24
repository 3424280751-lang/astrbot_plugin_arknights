"""Embedded Jinja2 card templates and the shared stylesheet."""

from __future__ import annotations

BASE_CSS = """/* Anime-forward Rhodes Island card system.
   Dark game UI foundations stay readable while softer colour, layered surfaces,
   and character-first framing keep the cards from feeling like control panels. */
:root {
  --space-1: 4px;
  --space-2: 8px;
  --space-3: 12px;
  --space-4: 16px;
  --space-5: 24px;
  --space-6: 32px;
  --radius-sm: 8px;
  --radius-md: 12px;
  --radius-lg: 16px;
  --panel-2: #1a1d2a;
  --ok: #80e4b0;
  --warn: #ffcf75;
  --bad: #ff91a3;

  --bg: #090b12;
  --panel: #11131d;
  --panel-alt: var(--panel-2);
  --panel-soft: rgba(24, 27, 40, 0.84);
  --line: rgba(226, 230, 244, 0.14);
  --line-soft: rgba(226, 230, 244, 0.08);
  --line-strong: rgba(255, 255, 255, 0.24);
  --text: #f8f7fb;
  --label: #b7bac9;
  --muted: #b1b8cc;
  --accent: #ff829f;
  --accent-2: #58d5e8;
  --accent-3: #ff718f;
  --danger: var(--bad);
  --theme: #ffc857;
  --theme-2: #58d5e8;
  --theme-soft: rgba(255, 200, 87, 0.13);
}
* {
  box-sizing: border-box;
  margin: 0;
  padding: 0;
}
body {
  display: inline-block;
  color: var(--text);
  background: var(--bg);
  font-family: "HarmonyOS Sans SC", "Microsoft YaHei", system-ui, sans-serif;

  font-size: 14px;

  line-height: 1.5;
}
.card {
  --accent-dim: color-mix(in srgb, var(--theme) 52%, transparent);
  width: 900px;
  padding: var(--space-6) 38px var(--space-5);
  position: relative;
  overflow: hidden;
  border: 1px solid var(--line-strong);
  border-radius: var(--radius-lg);
  font-variant-numeric: tabular-nums;
  background-color: var(--panel);
  background-image:
    linear-gradient(128deg, transparent 0 66%, var(--theme-soft) 66% 80%, transparent 80%),
    linear-gradient(90deg, rgba(255, 255, 255, 0.026) 1px, transparent 1px),
    linear-gradient(rgba(255, 255, 255, 0.026) 1px, transparent 1px),
    linear-gradient(150deg, rgba(255, 255, 255, 0.035), transparent 32%),
    linear-gradient(165deg, #151824 0%, #0b0d14 72%);
  background-size: auto, 48px 48px, 48px 48px, auto, auto;
}
.card::before {
  content: "";
  position: absolute;
  z-index: 2;
  top: 0;
  left: 0;
  right: 0;
  height: 4px;
  background: linear-gradient(90deg, var(--theme) 0 34%, var(--theme-2) 34% 47%, transparent 47%);
}
.card::after {
  content: "";
  position: absolute;
  z-index: 0;
  width: 270px;
  height: 180px;
  top: -106px;
  right: -44px;
  transform: rotate(13deg);
  border: 22px solid color-mix(in srgb, var(--theme-2) 12%, transparent);
  background: repeating-linear-gradient(
    90deg,
    color-mix(in srgb, var(--theme) 10%, transparent) 0 7px,
    transparent 7px 18px
  );
  pointer-events: none;
}
.card > * {
  position: relative;
  z-index: 1;
}
/* Each card family gets an anime UI colour identity instead of sharing one
   industrial amber treatment. */
.card.t-help {
  --theme: #63dcf0;
  --theme-2: #ff7fa0;
  --theme-soft: rgba(99, 220, 240, 0.11);
}
.card.t-profile {
  --theme: #ff829f;
  --theme-2: #62dbe9;
  --theme-soft: rgba(255, 130, 159, 0.12);
}
.card.t-sanity {
  --theme: #58d5e8;
  --theme-2: #ffd36d;
  --theme-soft: rgba(88, 213, 232, 0.12);
}
.card.t-operator {
  --theme: #ffca62;
  --theme-2: #ff718f;
  --theme-soft: rgba(255, 113, 143, 0.1);
}
.card.t-roster {
  --theme: #b6a1ff;
  --theme-2: #5cd7e8;
  --theme-soft: rgba(182, 161, 255, 0.11);
}
.card.t-building {
  --theme: #71dfb2;
  --theme-2: #ffd064;
  --theme-soft: rgba(113, 223, 178, 0.1);
}
.card.t-task,
.card.t-campaign {
  --theme: #62c7ff;
  --theme-2: #ffd163;
  --theme-soft: rgba(98, 199, 255, 0.1);
}
.card.t-recruit {
  --theme: #f2d06f;
  --theme-2: #7bded0;
  --theme-soft: rgba(242, 208, 111, 0.1);
}
.card.t-gacha {
  --theme: #ffd05f;
  --theme-2: #ff6f9d;
  --theme-soft: rgba(255, 111, 157, 0.115);
  background-image:
    radial-gradient(1.5px 1.5px at 9% 8%, rgba(255, 255, 255, 0.5), transparent),
    radial-gradient(1.2px 1.2px at 78% 13%, rgba(255, 208, 95, 0.46), transparent),
    radial-gradient(1px 1px at 38% 24%, rgba(255, 255, 255, 0.28), transparent),
    linear-gradient(128deg, transparent 0 66%, var(--theme-soft) 66% 80%, transparent 80%),
    linear-gradient(90deg, rgba(255, 255, 255, 0.022) 1px, transparent 1px),
    linear-gradient(rgba(255, 255, 255, 0.022) 1px, transparent 1px),
    linear-gradient(165deg, #171722 0%, #0b0d14 72%);
  background-size: 190px 190px, 230px 230px, 170px 170px, auto, 48px 48px, 48px 48px, auto;
}
.card.t-rogue {
  --theme: #bd8cff;
  --theme-2: #ff778e;
  --theme-soft: rgba(189, 140, 255, 0.11);
  background-image:
    linear-gradient(128deg, transparent 0 66%, var(--theme-soft) 66% 80%, transparent 80%),
    linear-gradient(90deg, rgba(255, 255, 255, 0.016) 1px, transparent 1px),
    linear-gradient(rgba(255, 255, 255, 0.016) 1px, transparent 1px),
    linear-gradient(165deg, #15131e 0%, #090b11 75%);
  background-size: auto, 52px 52px, 52px 52px, auto;
}
.card.t-announce {
  --theme: #77bfff;
  --theme-2: #a9a0ff;
  --theme-soft: rgba(119, 191, 255, 0.1);
}
.card.t-garrison {
  --theme: #4fd6c2;
  --theme-2: #ffd05f;
  --theme-soft: rgba(79, 214, 194, 0.12);
}
.card-header {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: 18px;
  padding: 0 0 var(--space-3);
  margin-bottom: var(--space-2);
  border-bottom: none;
}
.card-title {
  font-size: 28px;
  font-weight: 700;
  line-height: 1.5;
  letter-spacing: 1px;
}
.card-title::before {
  content: "";
  display: inline-block;
  width: 4px;
  height: 28px;
  margin-right: var(--space-3);
  background: linear-gradient(180deg, var(--accent), var(--accent-2));
  clip-path: none;
  vertical-align: -4px;

  border-radius: var(--radius-sm);
}
.card-subtitle {
  color: var(--muted);
  font-size: 12px;
  font-weight: 600;
  letter-spacing: 1.8px;
  text-transform: uppercase;
  padding-bottom: 2px;

  opacity: 0.9;

  line-height: 1.5;
}
.stripes {
  width: 100%;
  height: 2px;
  margin: 0 0 var(--space-5);
  border-radius: 3px;
  opacity: 1;
  background: linear-gradient(90deg, var(--accent), var(--accent-2));
}
.section {
  margin-bottom: 20px;
}
.section-title {
  display: flex;
  align-items: center;
  gap: 9px;
  color: var(--text);
  font-size: 16px;
  font-weight: 700;
  letter-spacing: 0.3px;
  margin-bottom: var(--space-3);
  padding-bottom: 0;
  border-bottom: none;

  line-height: 1.5;
}
.section-title::before {
  content: "";
  width: 3px;
  height: 16px;
  flex: none;
  background: var(--accent);
  clip-path: none;

  border-radius: var(--radius-sm);
}
.row {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 16px;
  min-height: 38px;
  padding: 8px 3px;
  border-bottom: 1px solid var(--line-soft);
  font-size: 15px;
}
.row:last-child {
  border-bottom: none;
}
.row-label {
  color: var(--label);
  letter-spacing: 0.3px;
  flex: none;
}
.row-value {
  color: var(--text);
  font-weight: 700;
  text-align: right;
}
.row-value.accent,
.stars {
  color: var(--theme);
}
.stars {
  letter-spacing: 1px;
}
.progress {
  height: 6px;
  margin: 7px 0 13px;
  position: relative;
  overflow: hidden;
  border-radius: var(--radius-sm);
  background: rgba(255,255,255,0.08);
}
.progress::after {
  content: "";
  position: absolute;
  inset: 0;
  background: none;
}
.progress-fill {
  height: 100%;
  border-radius: var(--radius-sm);
  background: linear-gradient(90deg, var(--accent), var(--accent-2));
}
.progress-fill.dim {
  opacity: 0.52;
}
.grid {
  display: flex;
  flex-wrap: wrap;
  gap: 12px;
}
.tile {
  width: 74px;
  position: relative;
  text-align: center;
}
.tile img {
  width: 68px;
  height: 68px;
  display: block;
  border: 1px solid var(--line);
  border-radius: 6px;
  background: linear-gradient(145deg, var(--theme-soft), var(--panel-alt));
  filter: saturate(1.08) contrast(1.02);
}
.tile .name {
  margin-top: 5px;
  color: var(--label);
  font-size: 12px;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}
.panel {
  position: relative;
  margin-bottom: 20px;
  padding: 14px 17px 15px;
  overflow: hidden;
  border: 1px solid var(--line);
  border-radius: var(--radius-md);
  background:
    linear-gradient(115deg, var(--theme-soft), transparent 28%),
    rgba(13, 15, 24, 0.74);
  box-shadow: 0 12px 30px rgba(0, 0, 0, 0.12);
}
.panel::before {
  content: "";
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 2px;
  background: linear-gradient(90deg, var(--theme), var(--theme-2) 26%, transparent 72%);
  opacity: 0.9;
}
.panel .section-title {
  margin-bottom: var(--space-3);
  padding-bottom: 0;
  border-bottom: none;
}
.panel .row:last-child,
.panel .progress:last-child {
  border-bottom: none;
}
.card-footer {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 18px;
  margin-top: 20px;
  padding-top: 13px;
  border-top: 1px solid var(--line);
  color: var(--muted);
  font-size: 12px;
  letter-spacing: 0.6px;
}
.barcode {
  display: none;
}
.serial {
  color: color-mix(in srgb, var(--theme) 72%, var(--label));
  font-size: 12px;
  letter-spacing: 1.1px;
}
.empty {
  color: var(--muted);
  font-size: 14px;
  padding: 12px 2px;

  text-align: center;

  line-height: 1.5;
}
.help-grid {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 5px 28px;
}
.help-group {
  min-height: 57px;
  padding: 8px 10px 8px 12px;
  border-left: 2px solid color-mix(in srgb, var(--theme) 44%, transparent);
  background: rgba(255, 255, 255, 0.018);
}
.help-command {
  color: var(--text);
  font-family: Menlo, Consolas, monospace;
  font-size: 13.5px;
  font-weight: 700;
  letter-spacing: 0;
}
.help-command::before {
  content: ">";
  color: var(--theme);
  margin-right: 7px;
}
.help-desc {
  color: var(--label);
  font-size: 12px;
  line-height: 1.5;
  margin: 4px 0 0 17px;
}
.tick {
  position: absolute;
  bottom: 0;
  left: 0;
  width: 72px;
  height: 5px;
  background: linear-gradient(90deg, var(--theme), var(--theme-2));
}
.tick.right {
  left: auto;
  right: 0;
}
/* Operator rarity language. Arknights reports rarity zero based in the API;
   templates receive display stars and use these three player-facing colours. */
.rarity-6 {
  --rarity-color: #ff8a2a;
  --rarity-soft: rgba(255, 138, 42, 0.22);
}
.rarity-5 {
  --rarity-color: #f8c800;
  --rarity-soft: rgba(248, 200, 0, 0.2);
}
.rarity-4 {
  --rarity-color: #a783d1;
  --rarity-soft: rgba(167, 131, 209, 0.22);
}
.tile.rarity-6 img,
.tile.rarity-5 img,
.tile.rarity-4 img,
.assistant.rarity-6 .assistant-art,
.assistant.rarity-5 .assistant-art,
.assistant.rarity-4 .assistant-art,
.detail.rarity-6 .detail-portrait,
.detail.rarity-5 .detail-portrait,
.detail.rarity-4 .detail-portrait,
.op.rarity-6 > img,
.op.rarity-5 > img,
.op.rarity-4 > img,
.op.rarity-6 .op-art,
.op.rarity-5 .op-art,
.op.rarity-4 .op-art {
  border: 2px solid var(--rarity-color);
  box-shadow: 0 0 0 1px var(--rarity-soft), 0 8px 24px var(--rarity-soft);
}
.assistant.rarity-6 .assistant-badge,
.assistant.rarity-5 .assistant-badge,
.assistant.rarity-4 .assistant-badge {
  border-color: var(--rarity-color);
}
.assistant.rarity-6 .assistant-name,
.assistant.rarity-5 .assistant-name,
.assistant.rarity-4 .assistant-name,
.detail.rarity-6 .detail-name,
.detail.rarity-5 .detail-name,
.detail.rarity-4 .detail-name,
.tile.rarity-6 .name,
.tile.rarity-5 .name,
.tile.rarity-4 .name,
.tile.rarity-6 .stars,
.tile.rarity-5 .stars,
.tile.rarity-4 .stars,
.op.rarity-6 .op-name,
.op.rarity-5 .op-name,
.op.rarity-4 .op-name,
.op.rarity-6 .op-pulls,
.op.rarity-5 .op-pulls,
.op.rarity-4 .op-pulls {
  color: var(--rarity-color);
}
.detail.rarity-6 .detail-name::before,
.detail.rarity-5 .detail-name::before,
.detail.rarity-4 .detail-name::before {
  background: var(--rarity-color);
}
.tile.rarity-6[data-rarity]::after,
.tile.rarity-5[data-rarity]::after,
.tile.rarity-4[data-rarity]::after {
  content: attr(data-rarity) "★";
  position: absolute;
  z-index: 2;
  top: 4px;
  right: 7px;
  padding: 1px 4px;
  border: 1px solid var(--rarity-color);
  border-radius: 3px;
  color: var(--rarity-color);
  background: rgba(8, 10, 17, 0.86);
  font-size: 12px;
  font-weight: 800;
  line-height: 18px;
}
/* Shared data shells used by the individual templates. */
.overview,
.summary,
.count,
.owned-bar,
.stat-strip,
.banner,
.theme,
.task-box,
.slot-card,
.rating,
.badge,
.clue,
.ann-tag,
.pity-pill {
  border-radius: 6px;
}
.overview,
.summary,
.count,
.owned-bar,
.stat-strip {
  overflow: hidden;
  background: rgba(13, 15, 24, 0.66);
}
.banner,
.theme,
.task-box,
.slot-card {
  overflow: hidden;
  background: rgba(13, 15, 24, 0.7);
}


/* Shared components use scoped selectors so card-local layouts retain their grids. */
.card .ui-header .ann-title { font-size: 28px; font-weight: 700; line-height: 1.5; }
.card .ui-header .id-level b { font-size: 12px; }
.card .ui-header .g-nm { font-size: 28px; font-weight: 700; }
.card .roster-head .ui-section { margin-bottom: 0; }
.card .ui-header h1 { font-size: 28px; font-weight: 700; line-height: 1.5; }
.card .ui-header .g-user { width: 100%; margin: 0; }
.card .ui-header:has(.g-user) { border-left: 3px solid var(--accent); padding-left: var(--space-3); }
.card .ui-section { font-size: 16px; font-weight: 700; margin-bottom: var(--space-3); }
.card .ui-metric { min-width: 0; font-variant-numeric: tabular-nums; }
.card .ui-metric .ui-label { display: block; font-size: 12px; color: var(--muted); line-height: 1.5; }
.card .ui-metric .ui-value { display: block; font-weight: 700; font-variant-numeric: tabular-nums; line-height: 1.5; }
.card .metrics .ui-metric, .card .stat-cell.ui-metric, .card .kpi .ui-metric, .card .sanity-block .ui-metric {
  background: var(--panel-2); border-radius: var(--radius-md); padding: var(--space-4);
}
.card .metrics .ui-value, .card .stat-cell .ui-value, .card .kpi .ui-value, .card .sanity-block .ui-value { font-size: 34px; }
.card .ui-metric .ui-unit { font-size: 14px; color: var(--muted); font-weight: 400; margin-left: var(--space-1); }
.card .ui-highlight .ui-value { color: var(--accent); }
.card .stat-strip { gap: var(--space-2); border: 0; background: none; overflow: visible; }
.card .stat-cell { border: 0; }
.card .stat-cell .ui-value { overflow-wrap: anywhere; }
.card .ui-progress-row { grid-template-columns: 120px 1fr 70px 54px; }
.card .ui-progress-row .bar, .card .op-mood { height: 6px; border-radius: var(--radius-sm); background: rgba(255,255,255,0.08); }
.card .ui-progress-row .bar i, .card .op-mood > div { height: 100%; border-radius: var(--radius-sm); background: linear-gradient(90deg,var(--accent),var(--accent-2)); }
.card .hint { font-size: 12px; color: var(--muted); border-left: 2px solid var(--line-strong); padding-left: var(--space-2); line-height: 1.5; }
.card table { border-collapse: collapse; font-variant-numeric: tabular-nums; }
.card table th { font-size: 12px; color: var(--muted); border-bottom: 1px solid var(--line); }
.card table tbody tr { height: 40px; }
.card table tbody tr:nth-child(even) { background: rgba(255,255,255,0.03); }
.card .g-table th, .card .g-table td { padding: var(--space-2); overflow: visible; text-overflow: clip; }
.card .g-table td:nth-child(5), .card .g-table td:nth-child(6), .card .g-table th:nth-child(5), .card .g-table th:nth-child(6) { text-align: right; }
.card .g-table td:last-child { white-space: normal; overflow-wrap: anywhere; }
.card .g-win, .card .g-lose, .card .g-badge { display: inline-block; padding: 2px 6px; border-radius: 6px; font-weight: 700; }
.card .g-win, .card .g-badge.win { color: var(--ok); background: rgba(128,228,176,0.12); }
.card .g-lose, .card .g-badge.lose { color: var(--bad); background: rgba(255,145,163,0.12); }
.card .g-bond.off { opacity: 1; border-style: dashed; }
.card .sanity-block { align-items: center; }
.card .sanity-block .ui-metric { flex: 1; }
.card .sanity-block .ui-value { color: var(--accent); }
"""

MACROS = """{% macro card_header(title, meta=None) -%}
<div class="card-header ui-header">
  {% if caller is defined %}{{ caller() }}{% else %}
  <div class="card-title">{{ title }}</div>
  {% if meta is not none %}<div class="card-subtitle">{{ meta }}</div>{% endif %}
  {% endif %}
</div>
<div class="stripes ui-divider"></div>
{%- endmacro %}

{% macro section(title) -%}
<div class="section-title ui-section">{{ title }}</div>
{%- endmacro %}

{% macro metric(label, value, unit="", highlight=False, classes="metric", label_class="row-label", value_class="") -%}
<div class="{{ classes }} ui-metric{% if highlight %} ui-highlight{% endif %}">
  <div class="{{ label_class }} ui-label">{{ label }}</div>
  <b class="{{ value_class }} ui-value">{{ value }}{% if unit %}<small class="ui-unit">{{ unit }}</small>{% endif %}</b>
</div>
{%- endmacro %}

{% macro progress_row(label, cur, total, percent) -%}
<div class="row ui-progress-row">
  <span class="nm">{{ label }}</span>
  <span class="bar"><i style="width: {{ percent }}%"></i></span>
  <span class="num">{{ cur }} / <b>{{ total }}</b></span>
  <span class="rate">{{ percent }}%</span>
</div>
{%- endmacro %}
"""

TEMPLATES: dict[str, str] = {
    "announce.html": """{% import "_macros.html" as ui %}
<!doctype html>
<html lang="zh-CN">
  <head>
    <meta charset="utf-8" />
    <style>
      {{ base_css | safe }}
      .ann {
        display: flex;
        align-items: flex-start;
        gap: 12px;
        padding: 11px 2px;
        border-bottom: 1px solid var(--line-soft);
      }
      .ann:last-child {
        border-bottom: none;
      }
      .ann-id {
        flex: none;
        width: 54px;
        font-size: 12px;
        color: var(--muted);
        letter-spacing: 0.6px;
        padding-top: 2px;
      }
      .ann-body {
        flex: 1;
        min-width: 0;
      }
      .ann-title {
        font-size: 15px;
        font-weight: 600;
        line-height: 1.5;
      }
      .ann-date {
        font-size: 12px;
        color: var(--muted);
        margin-top: 3px;
      }
      .ann-tag {
        flex: none;
        font-size: 12px;
        letter-spacing: 1.2px;
        padding: 2px 8px;
        border: 1px solid var(--line);
        color: var(--label);
        margin-top: 1px;
      }
      .ann-tag.act {
        border-color: var(--accent);
        color: var(--accent);
      }
      .count {
        display: flex;
        border: 1px solid var(--line);
        margin-bottom: 18px;
      }
      .count-cell {
        flex: 1;
        padding: 9px 14px;
        border-right: 1px solid var(--line);
        font-size: 12px;
        color: var(--muted);
        letter-spacing: 1.3px;
      }
      .count-cell:last-child {
        border-right: none;
      }
      .count-cell b {
        display: block;
        font-size: 20px;
        color: var(--text);
        margin-top: 3px;
        letter-spacing: 0;
      }
    </style>
  </head>
  <body>
    <div class="card {{ card_class }}">
      {% set header_title %}官方公告{% endset %}{% set header_meta %}Announcements{% endset %}
{{ ui.card_header(header_title, header_meta) }}
      <div class="count">
        <div class="count-cell">公告总数<b>{{ announce.total }}</b></div>
        <div class="count-cell">活动类<b>{{ announce.activity_count }}</b></div>
        <div class="count-cell">系统类<b>{{ announce.system_count }}</b></div>
      </div>
      {% for item in announce.records %}
      <div class="ann">
        <span class="ann-id">#{{ item.id }}</span>
        <span class="ann-body">
          <span class="ann-title">{{ item.title }}</span>
          <span class="ann-date">{{ item.date_text or "时间未知" }}</span>
        </span>
        <span class="ann-tag {% if item.group == 'ACTIVITY' %}act{% endif %}">
          {{ item.group_cn }}
        </span>
      </div>
      {% endfor %}
      <div class="card-footer">
        <span>© HYPERGRYPH · 用 `ark公告 &lt;编号&gt;` 查看正文；`ark订阅公告` 可推送新公告</span>
        <span><span class="barcode"></span><span class="serial">RI-NEWS-001</span></span>
      </div>
    </div>
  </body>
</html>
""",
    "announce_detail.html": """{% import "_macros.html" as ui %}
<!doctype html>
<html lang="zh-CN">
  <head>
    <meta charset="utf-8" />
    <style>
      {{ base_css | safe }}
      .ann-head {
        margin-bottom: 4px;
      }
      .ann-title {
        font-size: 25px;
        font-weight: 700;
        line-height: 1.5;
        letter-spacing: 0.5px;
      }
      .ann-title::before {
        content: "";
        display: inline-block;
        width: 6px;
        height: 22px;
        margin-right: 11px;
        background: var(--accent);
        vertical-align: -2px;
      }
      .ann-meta {
        display: flex;
        align-items: center;
        gap: 10px;
        margin: 10px 0 0;
        font-size: 12px;
        color: var(--muted);
        letter-spacing: 1px;
      }
      .ann-meta .tag {
        font-size: 12px;
        letter-spacing: 1.2px;
        padding: 2px 8px;
        border: 1px solid var(--accent);
        color: var(--accent);
      }
      /* The body is the site's own rich text: paragraphs, emphasis and inline
         artwork. Only the outer frame comes from this plugin. */
      .body {
        font-size: 14.5px;
        line-height: 1.85;
        color: var(--text);
        word-break: break-word;
      }
      .body p {
        margin: 0 0 0.85em;
      }
      .body strong,
      .body b {
        color: var(--accent);
        font-weight: 700;
      }
      .body em {
        color: var(--label);
      }
      .body img {
        display: block;
        max-width: 100%;
        height: auto;
        margin: 0.9em auto;
        border: 1px solid var(--line);
      }
      .body br {
        line-height: 1.85;
      }
      .body a {
        color: var(--accent);
        text-decoration: none;
        word-break: break-all;
      }
    </style>
  </head>
  <body>
    <div class="card {{ card_class }}">
      {% call ui.card_header("") %}<div class="ann-head">
        <div class="ann-title">{{ announce.title }}</div>
        <div class="ann-meta">
          <span class="tag">{{ announce.group_cn }}</span>
          <span>{{ announce.date_text or "时间未知" }}</span>
          {% if announce.author %}<span>{{ announce.author }}</span>{% endif %}
          <span style="margin-left: auto">编号 {{ announce.id }}</span>
        </div>
      </div>
      {% endcall %}
      <div class="panel" style="margin-bottom: 0">
        <div class="body">{{ announce.body_html | safe }}</div>
      </div>
      <div class="card-footer">
        <span>© HYPERGRYPH · 共 {{ announce.image_total }} 张配图</span>
        <span><span class="barcode"></span><span class="serial">RI-NEWS-{{ announce.id }}</span></span>
      </div>
    </div>
  </body>
</html>
""",
    "building.html": """{% import "_macros.html" as ui %}
<!doctype html>
<html lang="zh-CN">
  <head>
    <meta charset="utf-8" />
    <style>
      {{ base_css | safe }}
      .overview {
        display: flex;
        border: 1px solid var(--line);
        margin-bottom: 20px;
      }
      .overview-cell {
        flex: 1;
        padding: 10px 14px;
        border-right: 1px solid var(--line);
      }
      .overview-cell:last-child {
        border-right: none;
      }
      .overview-key {
        font-size: 12px;
        color: var(--muted);
        letter-spacing: 1.3px;
      }
      .overview-val {
        font-size: 19px;
        font-weight: 700;
        margin-top: 4px;
      }
      .overview-val small {
        font-size: 12px;
        color: var(--muted);
        font-weight: 400;
      }
      .section-title img {
        width: 19px;
        height: 19px;
        vertical-align: -4px;
        margin-right: 7px;
      }
      .slot {
        display: flex;
        align-items: center;
        gap: 12px;
        padding: 8px 0;
        border-bottom: 1px solid var(--line-soft);
      }
      .slot:last-child {
        border-bottom: none;
      }
      .slot-level {
        flex: none;
        width: 52px;
        font-size: 12px;
        letter-spacing: 1px;
        color: var(--accent);
        border: 1px solid var(--line);
        text-align: center;
        padding: 3px 0;
      }
      .slot-ops {
        display: flex;
        gap: 14px;
        flex-wrap: wrap;
        flex: 1;
      }
      .op {
        display: flex;
        align-items: center;
        gap: 7px;
        width: 158px;
      }
      .op img {
        width: 34px;
        height: 34px;
        border: 1px solid var(--line);
        flex: none;
      }
      .op-body {
        flex: 1;
        min-width: 0;
      }
      .op-name {
        font-size: 12px;
        white-space: nowrap;
        overflow: hidden;
        text-overflow: ellipsis;
      }
      .op-mood {
        height: 4px;
        background: #1d2027;
        margin-top: 4px;
      }
      .op-mood div {
        height: 100%;
        background: var(--accent);
      }
      .op-mood.low div {
        background: var(--danger);
      }
      .clue-list {
        display: flex;
        gap: 6px;
        flex-wrap: wrap;
      }
      .clue {
        font-size: 12px;
        border: 1px solid var(--line);
        color: var(--label);
        padding: 2px 8px;
      }
      .clue.held {
        border-color: var(--accent);
        color: var(--accent);
      }
      .facility-stat {
        font-size: 12px;
        color: var(--label);
        overflow-wrap: anywhere;
      }
      .training-value {
        min-width: 0;
        text-align: right;
        overflow-wrap: anywhere;
      }
    </style>
  </head>
  <body>
    <div class="card {{ card_class }}">
      {% set header_title %}基建{% endset %}{% set header_meta %}Infrastructure{% endset %}
{{ ui.card_header(header_title, header_meta) }}
      <div class="overview">
        <div class="overview-cell">
          <div class="overview-key">无人机</div>
          <div class="overview-val">
            {{ building.labor.value }}<small> / {{ building.labor.max }}</small>
          </div>
        </div>
        <div class="overview-cell">
          <div class="overview-key">线索持有</div>
          <div class="overview-val">
            {{ building.clue.own }}<small> 已收 {{ building.clue.received }}</small>
          </div>
        </div>
        <div class="overview-cell">
          <div class="overview-key">每日线索奖励</div>
          <div class="overview-val">
            {% if building.clue.daily_reward %}已领取{% else %}未领取{% endif %}
          </div>
        </div>
        <div class="overview-cell">
          <div class="overview-key">线索交流</div>
          <div class="overview-val">
            {% if building.clue.sharing %}进行中{% else %}未开启{% endif %}
          </div>
        </div>
      </div>
      {% for facility in building.facilities %}
      <div class="panel">
        {% set section_title %}
          {% if facility.icon %}<img src="{{ facility.icon }}" alt="" />{% endif
          %}{{ facility.name }}
        {% endset %}{{ ui.section(section_title) }}
        {% if facility.key == 'meeting' %}
        <div class="row facility-stat">
          <span class="row-label">线索交流剩余:</span>
          <span class="row-value">{% if building.exchange.sharing %}{{ building.exchange.share_remaining_text or '未提供' }}{% else %}未在交流{% endif %}</span>
        </div>
        {% endif %}
        {% for slot in facility.slots %}
        <div class="slot">
          <div class="slot-level">Lv.{{ slot.level }}</div>
          <div class="slot-ops">
            {% for op in slot.operators %}
            <div class="op rarity-{{ op.stars }}">
              <img src="{{ op.avatar }}" alt="{{ op.name }}" />
              <div class="op-body">
                <div class="op-name">{{ op.name }}</div>
                <div class="op-mood {% if op.mood_percent < 35 %}low{% endif %}">
                  <div style="width: {{ op.mood_percent }}%"></div>
                </div>
              </div>
            </div>
            {% endfor %}
            {% if not slot.operators %}
            <div class="empty" style="padding: 4px 0">空闲</div>
            {% endif %}
          </div>
        </div>
        {% endfor %}
      </div>
      {% endfor %}
      {% if building.recycle is not none %}
      <div class="panel">
        {% set section_title %}回收站{% endset %}{{ ui.section(section_title) }}
        <div class="row facility-stat">
          <span class="row-label">等级</span>
          <span class="row-value">{% if building.recycle.level is not none %}Lv.{{ building.recycle.level }}{% else %}未提供{% endif %}</span>
        </div>
        {% for slot in building.recycle.slots %}
        <div class="slot">
          <div class="slot-level">Lv.{{ slot.level }}</div>
          <div class="slot-ops">
            {% for op in slot.operators %}
            <div class="op rarity-{{ op.stars }}">
              <img src="{{ op.avatar }}" alt="{{ op.name }}" />
              <div class="op-body">
                <div class="op-name">{{ op.name }}</div>
                <div class="op-mood {% if op.mood_percent < 35 %}low{% endif %}">
                  <div style="width: {{ op.mood_percent }}%"></div>
                </div>
              </div>
            </div>
            {% endfor %}
            {% if not slot.operators %}<div class="empty" style="padding: 4px 0">空闲</div>{% endif %}
          </div>
        </div>
        {% endfor %}
        {% if building.recycle.remain_text is not none %}
        <div class="row facility-stat">
          <span class="row-label">下次产出</span>
          <span class="row-value">{{ building.recycle.remain_text }}</span>
        </div>
        {% endif %}
        <div class="row facility-stat">
          <span class="row-label">储藏空间</span>
          <span class="row-value">{{ building.recycle.storage if building.recycle.storage is not none else '未提供' }}/{{ building.recycle.max if building.recycle.max is not none else '未提供' }}</span>
        </div>
      </div>
      {% endif %}
      <div class="panel">
        {% set section_title %}其他{% endset %}{{ ui.section(section_title) }}
        <div class="row">
          <span class="row-label">线索板</span>
          <span class="clue-list">
            {% for item in building.clue.board %}
            <span class="clue held">{{ item }}</span>
            {% endfor %}
            {% if not building.clue.board %}
            <span class="row-value" style="color: var(--muted)">无</span>
            {% endif %}
          </span>
        </div>
        <div class="row">
          <span class="row-label">办公室刷新次数</span>
          <span class="row-value">{{ building.hire.refresh }}</span>
        </div>
        <div class="row">
          <span class="row-label">训练室</span>
          <span class="row-value training-value">
            训练位: {{ building.training.trainee or '空闲' }} / 教官: {{ building.training.trainer or '空闲' }}
            <div class="facility-stat">剩余训练时间: {% if building.training.active %}{{ building.training.remain_text }}{% else %}无训练中{% endif %}</div>
          </span>
        </div>
      </div>
      <div class="card-footer">
        <span>© HYPERGRYPH · 心情上限 {{ building.mood_max }}，按干员心情值换算</span>
        <span><span class="barcode"></span><span class="serial">RI-INFRA-001</span></span>
      </div>
    </div>
  </body>
</html>
""",
    "campaign.html": """{% import "_macros.html" as ui %}
<!doctype html>
<html lang="zh-CN">
  <head>
    <meta charset="utf-8" />
    <style>
      {{ base_css | safe }}
      .reward-block {
        display: flex;
        align-items: baseline;
        gap: 14px;
        margin: 2px 0 14px;
      }
      .reward-value {
        font-size: 60px;
        font-weight: 700;
        line-height: 1.5;
        color: var(--theme);
        letter-spacing: 0;
      }
      .reward-max {
        font-size: 19px;
        color: var(--muted);
        font-weight: 600;
      }
      .reward-tag {
        margin-left: auto;
        font-size: 12px;
        letter-spacing: 1.6px;
        padding: 5px 13px;
        border: 1px solid var(--line);
        color: var(--label);
      }
      .map-row {
        display: flex;
        align-items: center;
        gap: 12px;
        padding: 9px 2px;
        border-bottom: 1px solid var(--line-soft);
      }
      .map-row:last-child {
        border-bottom: none;
      }
      .map-name {
        flex: 1;
        font-size: 14px;
      }
      .map-zone {
        font-size: 12px;
        color: var(--muted);
        margin-left: 8px;
      }
      .map-kills {
        font-size: 15px;
        font-weight: 700;
        width: 74px;
        text-align: right;
      }
      .map-row.done .map-kills {
        color: var(--accent);
      }
      .map-mark {
        flex: none;
        width: 46px;
        font-size: 12px;
        letter-spacing: 1px;
        text-align: center;
        padding: 2px 0;
        border: 1px solid var(--line);
        color: var(--muted);
      }
      .map-row.done .map-mark {
        border-color: var(--accent);
        color: var(--accent);
      }
    </style>
  </head>
  <body>
    <div class="card {{ card_class }}">
      {% set header_title %}剿灭作战{% endset %}{% set header_meta %}Annihilation{% endset %}
{{ ui.card_header(header_title, header_meta) }}
      <div class="panel">
        {% set section_title %}本周合成玉{% endset %}{{ ui.section(section_title) }}
        <div class="reward-block">
          <span class="reward-value">{{ campaign.reward.current }}</span>
          <span class="reward-max">/ {{ campaign.reward.total }}</span>
          <span class="reward-tag">
            {{ campaign.cleared }} / {{ campaign.total }} 已满击杀
          </span>
        </div>
        <div class="progress">
          <div class="progress-fill" style="width: {{ campaign.reward.percent }}%"></div>
        </div>
      </div>
      <div class="panel">
        {% set section_title %}作战记录{% endset %}{{ ui.section(section_title) }}
        {% if campaign.records %}
        {% for record in campaign.records %}
        <div class="map-row {% if record.max_kills >= 400 %}done{% endif %}">
          <span class="map-name">
            {{ record.name }}
            {% if record.zone %}<span class="map-zone">{{ record.zone }}</span>{% endif %}
          </span>
          <span class="map-mark">
            {% if record.max_kills >= 400 %}满击杀{% else %}未满{% endif %}
          </span>
          <span class="map-kills">{{ record.max_kills }}</span>
        </div>
        {% endfor %}
        {% else %}
        <div class="empty">暂无剿灭记录</div>
        {% endif %}
      </div>
      <div class="card-footer">
        <span>© HYPERGRYPH · 满击杀为 400 杀，未满击杀无法获得全部合成玉</span>
        <span><span class="barcode"></span><span class="serial">RI-CAMPAIGN-001</span></span>
      </div>
    </div>
  </body>
</html>
""",
    "dps.html": """{% import "_macros.html" as ui %}
<!doctype html>
<html lang="zh-CN"><head><meta charset="utf-8"><style>
{{ base_css | safe }}
.metrics { display:flex; gap:18px; margin:24px 0; }
.metric { flex:1; padding:20px; border:1px solid var(--line); border-radius:8px; }
.metric b { display:block; font-size:40px; color:var(--theme); margin-top:8px; }
.details { display:grid; grid-template-columns:1fr 1fr; gap:0 28px; }
</style></head><body><div class="card {{ card_class }}">
{% call ui.card_header("") %}<div>{% set section_title %}DPS 查询 · 罗德岛终端{% endset %}{{ ui.section(section_title) }}<h1>{{ title }}</h1></div>{% endcall %}
<div class="metrics">{% for key in ['DPS','总伤','质量'] %}{% set metric_label %}{{ key }}{% endset %}{% set metric_value %}{{ dps[key] }}{% endset %}{{ ui.metric(metric_label, metric_value) }}{% endfor %}</div>
<div class="panel details"><div class="row"><span class="row-label">DPS 排名</span><span class="row-value">{% if dps_rank %}{{ dps_rank }} / {{ dps_rank_total }}{% else %}—{% endif %}</span></div>
<div class="row"><span class="row-label">总伤排名</span><span class="row-value">{% if dps['总伤'] != '不适用' and dmg_rank %}{{ dmg_rank }} / {{ dmg_rank_total }}{% else %}—{% endif %}</span></div>
{% for key in ['持续','初动','回转','部署费用','DPH','攻击间隔','目标数','职业','上线时间'] %}<div class="row"><span class="row-label">{{ key }}</span><span class="row-value">{{ dps[key] }}</span></div>{% endfor %}</div>
{% if stale %}<div class="empty">缓存数据已过期，请留意数据时间</div>{% endif %}
<div class="card-footer"><div>标准计算条件 · ark-dps.com · 数据 {{ updated }}<br>总伤排名：≥ 取下限参与，不适用不参与（全表 {{ total }} 条）</div></div>
</div></body></html>
""",
    "dps_multi.html": """{% import "_macros.html" as ui %}
﻿<!doctype html>
<html lang="zh-CN"><head><meta charset="utf-8"><style>
{{ base_css | safe }}
.skill-row { display:grid; grid-template-columns:minmax(180px,1fr) 110px 140px 120px 120px; gap:16px; padding:12px 0 18px; align-items:start; }
.skill-name { min-width:0; font-size:19px; line-height:1.6; }
.skill-name b { display:block; margin-top:8px; }
.metric { min-width:0; text-align:right; }
.skill-row .row-label { display:block; font-size:12px; color:var(--label); }
.metric b { display:block; font-size:26px; margin-top:8px; font-variant-numeric:tabular-nums; white-space:nowrap; }
.metric b.not-applicable { font-size:16px; line-height:31px; }
.highest { border-color:var(--theme); background:var(--theme-soft); }
.highest .skill-name, .highest .metric b { color:var(--theme); }
.highest-tag { display:inline-block; font-size:12px; padding:1px 7px; margin-left:8px; border:1px solid var(--theme); border-radius:4px; }
.skill-details { color:var(--label); font-size:12px; padding-top:12px; line-height:1.7; }
h1 { font-size:34px; margin-bottom:8px; }
</style></head><body><div class="card {{ card_class }}">
{% call ui.card_header("") %}<div>{% set section_title %}DPS 查询 · 罗德岛终端{% endset %}{{ ui.section(section_title) }}<h1>{{ operator }}</h1><div class="card-subtitle">共 {{ rows|length }} 个技能</div></div>{% endcall %}
{% for row in rows %}
<div class="panel{% if row.highest %} highest{% endif %}">
<div class="row skill-row"><div class="skill-name"><span class="row-label">技能</span><b>{{ row.label }}{% if row.highest %}<span class="highest-tag">最高</span>{% endif %}</b></div>
{% set metric_label %}DPS{% endset %}{% set metric_value %}{{ row.get('DPS') or '—' }}{% endset %}{{ ui.metric(metric_label, metric_value) }}
{{ ui.metric("总伤", row.get("总伤") or "—", value_class="not-applicable" if row.get("总伤") == "不适用" else "") }}
{% set metric_label %}DPS 排名{% endset %}{% set metric_value %}{% if row.dps_rank %}{{ row.dps_rank }} / {{ row.dps_rank_total }}{% else %}—{% endif %}{% endset %}{{ ui.metric(metric_label, metric_value) }}
{% set metric_label %}总伤排名{% endset %}{% set metric_value %}{% if row.get('总伤') != '不适用' and row.dmg_rank %}{{ row.dmg_rank }} / {{ row.dmg_rank_total }}{% else %}—{% endif %}{% endset %}{{ ui.metric(metric_label, metric_value) }}
</div>
<div class="skill-details">{% for key in ['持续','初动','回转','部署费用','职业'] %}{{ key }} {{ row.get(key) or '—' }}{% if not loop.last %} / {% endif %}{% endfor %}</div>
</div>
{% endfor %}
<div class="card-footer"><div>标准计算条件 · ark-dps.com · 数据 {{ updated }}<br>总伤排名：≥ 取下限参与，不适用不参与（全表 {{ total }} 条）</div></div>
{% if stale %}<div class="empty">缓存数据已过期，请留意数据时间</div>{% endif %}
</div></body></html>
""",
    "gacha.html": """{% import "_macros.html" as ui %}
<!doctype html>
<html lang="zh-CN">
  <head>
    <meta charset="utf-8" />
    <style>
      {{ base_css | safe }}
      .overview {
        display: flex;
        border: 1px solid var(--line);
        margin-bottom: 22px;
      }
      .overview-cell {
        flex: 1;
        padding: 11px 14px;
        border-right: 1px solid var(--line);
      }
      .overview-cell:last-child {
        border-right: none;
      }
      .overview-key {
        font-size: 12px;
        color: var(--muted);
        letter-spacing: 1.4px;
      }
      .overview-val {
        font-size: 23px;
        font-weight: 700;
        margin-top: 4px;
      }
      .overview-val small {
        font-size: 12px;
        color: var(--muted);
        font-weight: 400;
      }
      .overview-val.hot {
        color: var(--accent);
      }
      .overview-meta {
        font-size: 12px;
        color: var(--muted);
        margin-top: 3px;
      }
      /* ---- one section per banner family ---- */
      .banner {
        border: 1px solid var(--line);
        margin-bottom: 16px;
      }
      .banner-head {
        display: flex;
        align-items: center;
        gap: 12px;
        padding: 11px 15px;
        background: var(--panel-alt);
        border-bottom: 1px solid var(--line);
      }
      .banner-name {
        flex: 1;
        font-size: 16px;
        font-weight: 700;
        letter-spacing: 0.8px;
      }
      .banner-tag {
        font-size: 12px;
        letter-spacing: 1.1px;
        padding: 2px 7px;
        border: 1px solid var(--line);
        color: var(--label);
        flex: none;
      }
      .banner-name::before {
        content: "";
        display: inline-block;
        width: 4px;
        height: 15px;
        margin-right: 9px;
        background: var(--accent);
        vertical-align: -2px;
      }
      .pity-pill {
        font-size: 12px;
        padding: 4px 12px;
        border: 1px solid var(--accent);
        color: var(--accent);
        letter-spacing: 0.5px;
      }
      .pity-pill b {
        font-size: 15px;
      }
      .banner-date {
        line-height: 1.5;
        font-size: 12px;
        color: var(--muted);
        padding: 7px 15px 0;
        letter-spacing: 0.5px;
      }
      .banner-body {
        display: flex;
        align-items: stretch;
        gap: 14px;
        padding: 12px 15px 4px;
      }
      .banner-stats {
        display: flex;
        flex: 1;
        border: 1px solid var(--line);
      }
      .bstat {
        flex: 1;
        padding: 9px 13px;
        border-right: 1px solid var(--line);
      }
      .bstat:last-child {
        border-right: none;
      }
      .bstat-key {
        font-size: 12px;
        color: var(--muted);
        letter-spacing: 1.3px;
      }
      .bstat-val {
        font-size: 21px;
        font-weight: 700;
        margin-top: 3px;
      }
      .bstat-val.accent {
        color: var(--accent);
      }
      .rating {
        width: 118px;
        flex: none;
        border: 1px solid var(--line);
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 16px;
        font-weight: 700;
        letter-spacing: 1px;
        color: var(--accent);
        text-align: center;
        padding: 4px;
      }
      .rating.none {
        color: var(--muted);
        font-size: 12px;
        font-weight: 400;
        letter-spacing: 0.5px;
      }
      .ops {
        display: flex;
        flex-wrap: wrap;
        gap: 11px;
        padding: 12px 15px 15px;
      }
      .op {
        width: 108px;
        text-align: center;
      }
      .op-art {
        position: relative;
        width: 108px;
        height: 142px;
        border: 1px solid var(--line);
        background: linear-gradient(180deg, #1e232c 0%, #0f1114 100%);
        overflow: hidden;
      }
      .op-art img {
        width: 100%;
        height: 100%;
        object-fit: cover;
        object-position: center top;
        display: block;
      }
      .op-art .up,
      .op-art .off {
        position: absolute;
        top: 0;
        left: 0;
        font-size: 12px;
        font-weight: 700;
        padding: 1px 6px;
        letter-spacing: 0.5px;
      }
      .op-art .up {
        background: var(--accent);
        color: #0a0b0d;
      }
      .op-art .off {
        background: var(--danger);
        color: #0a0b0d;
      }
      .op-pulls {
        font-size: 12px;
        color: var(--accent);
        font-weight: 700;
        margin-top: 4px;
      }
      .op-name {
        font-size: 12px;
        color: var(--label);
        white-space: nowrap;
        overflow: hidden;
        text-overflow: ellipsis;
      }
      .note {
        font-size: 12px;
        color: var(--muted);
        padding: 0 15px 12px;
      }
    </style>
  </head>
  <body>
    <div class="card {{ card_class }}">
      {% set header_title %}抽卡分析{% endset %}{% set header_meta %}Headhunting Report{% endset %}
{{ ui.card_header(header_title, header_meta) }}
      <div class="overview">
        <div class="overview-cell">
          <div class="overview-key">总抽数</div>
          <div class="overview-val">{{ gacha.total }}</div>
        </div>
        <div class="overview-cell">
          <div class="overview-key">六星</div>
          <div class="overview-val hot">{{ gacha.six_total }}</div>
          <div class="overview-meta">五星 {{ gacha.five_total }}</div>
        </div>
        <div class="overview-cell">
          <div class="overview-key">平均出六</div>
          <div class="overview-val">{{ gacha.avg_six }}<small> 抽</small></div>
          <div class="overview-meta">整体口径</div>
        </div>
        <div class="overview-cell">
          <div class="overview-key">卡池数</div>
          <div class="overview-val">{{ gacha.banner_count }}</div>
          <div class="overview-meta">
            {% if gacha.just_synced %}本次已同步官网{% else %}使用本地记录{% endif %}
          </div>
        </div>
      </div>
      {% for banner in gacha.banners %}
      <div class="banner">
        <div class="banner-head">
          <span class="banner-name">{{ banner.label }}</span>
          <span class="banner-tag">{{ banner.family }}</span>
          <span class="pity-pill">已 <b>{{ banner.pity }}</b> 抽未出六星</span>
        </div>
        <div class="banner-date">
          {{ banner.date_range }}{% if banner.up_names %} · UP {{ banner.up_names | join(" / ") }}{% endif %}
        </div>
        <div class="banner-body">
          <div class="banner-stats">
            <div class="bstat">
              <div class="bstat-key">平均出六</div>
              <div class="bstat-val accent">
                {{ banner.avg_six if banner.six_total else "—" }}
              </div>
            </div>
            <div class="bstat">
              <div class="bstat-key">平均UP</div>
              <div class="bstat-val">
                {% if banner.up_known and banner.up_hits %}{{ banner.avg_up }}{% else %}—{% endif %}
              </div>
            </div>
            <div class="bstat">
              <div class="bstat-key">总抽数</div>
              <div class="bstat-val">{{ banner.total }}</div>
            </div>
          </div>
          {% if banner.luck %}
          <div class="rating">{{ banner.luck }}</div>
          {% else %}
          <div class="rating none empty">暂无六星</div>
          {% endif %}
        </div>
        {% if banner.six_stars %}
        <div class="ops">
          {% for item in banner.six_stars %}
          <div class="op rarity-{{ item.stars }}">
            <div class="op-art">
              <img src="{{ item.portrait or item.avatar }}" alt="{{ item.name }}" />
              {% if item.is_up is sameas true %}
              <span class="up">UP!</span>
              {% elif item.is_up is sameas false %}
              <span class="off">歪</span>
              {% endif %}
            </div>
            <div class="op-pulls">{{ item.pulls }} 抽</div>
            <div class="op-name">{{ item.name }}</div>
          </div>
          {% endfor %}
        </div>
        {% else %}
        <div class="note hint">该卡池暂无六星记录</div>
        {% endif %}
        {% if not banner.up_known %}
        <div class="note hint">
          {{ banner.up_note or "该卡池没有可用的 UP 名单，因此不做 UP / 歪判定" }}
        </div>
        {% elif not banner.five_total %}
        <div class="note hint">该卡池暂无五星记录</div>
        {% endif %}
      </div>
      {% endfor %}
      <div class="card-footer">
        <span>
          © HYPERGRYPH · 本地共 {{ gacha.stored_total }} 条 · 同步于
          {{ gacha.synced_text }}
        </span>
        <span><span class="barcode"></span><span class="serial">RI-HEADHUNT-001</span></span>
      </div>
    </div>
  </body>
</html>
""",
    "garrison_list.html": """{% import "_macros.html" as ui %}
<!doctype html>
<html lang="zh-CN">
  <head>
    <meta charset="utf-8" />
    <style>
      {{ base_css | safe }}
      .g-user {
        display: flex;
        align-items: center;
        gap: 12px;
        margin: 18px 0 14px;
        padding: 13px 16px;
        border: 1px solid var(--line);
        border-radius: 10px;
        background: var(--panel-alt);
      }
      .g-avatar {
        width: 44px;
        height: 44px;
        border-radius: 50%;
        border: 2px solid var(--line-strong);
        object-fit: cover;
        flex: none;
      }
      .g-who { min-width: 0; flex: 1; }
      .g-name { font-size: 16px; font-weight: 700; }
      .g-sub { margin-top: 3px; font-size: 12px; color: var(--label); }
      .g-secretary {
        display: flex;
        align-items: center;
        gap: 7px;
        padding: 5px 12px;
        border: 1px solid var(--line);
        border-radius: 18px;
        background: var(--panel-soft);
        font-size: 13px;
        flex: none;
      }
      .g-secretary img { width: 24px; height: 24px; border-radius: 50%; }
      .g-secretary span { color: var(--muted); font-size: 12px; }
      .g-summary { margin-bottom: 14px; font-size: 14px; color: var(--label); }
      .g-table {
        width: 100%;
        table-layout: fixed;
        border-collapse: collapse;
        background: var(--panel-soft);
        font-size: 13px;
      }
      .g-table th, .g-table td {
        padding: 10px 8px;
        text-align: left;
        border-bottom: 1px solid var(--line-soft);
      }
      .g-table th { color: var(--label); font-weight: 600; background: var(--panel-alt); }
      .g-table tbody tr:nth-child(even) { background: rgba(255, 255, 255, 0.025); }
      .g-table .g-win { color: #65d8a0; font-weight: 700; }
      .g-table .g-lose { color: var(--danger); font-weight: 700; }
      .g-table th, .g-table td, .g-name, .g-sub {
        white-space: nowrap;
        overflow: hidden;
        text-overflow: ellipsis;
      }
    </style>
  </head>
  <body>
    <div class="card t-garrison">
      {% set header_title %}卫戍战绩列表{% endset %}{% set header_meta %}规程 · {{ garrison.version }}{% endset %}
{{ ui.card_header(header_title, header_meta) }}
      <div class="g-user">
        {% if garrison.user.avatar %}
        <img class="g-avatar" src="{{ garrison.user.avatar }}" alt="" />
        {% endif %}
        <div class="g-who">
          <div class="g-name">{{ garrison.user.name or '—' }}</div>
          <div class="g-sub">uid {{ garrison.user.uid }} · Lv{{ garrison.user.level }} · {{ garrison.season_name }} · {{ garrison.version }} · {{ garrison.phase_name }}</div>
        </div>
        {% if garrison.user.secretary_name %}
        <div class="g-secretary">
          {% if garrison.user.secretary_icon %}
          <img src="{{ garrison.user.secretary_icon }}" alt="" />
          {% endif %}
          <span>助理</span>{{ garrison.user.secretary_name }}
        </div>
        {% endif %}
      </div>
      <div class="g-summary">共 {{ garrison.summary.total }} 场 · 显示最近 {{ garrison.summary.shown }} 场 · 通关 {{ garrison.summary.cleared }} 场（{{ garrison.summary.cleared_percent }}%）</div>
      <table class="g-table">
        <colgroup>
          <col style="width: 118px" />
          <col style="width: 54px" />
          <col style="width: 54px" />
          <col style="width: 54px" />
          <col style="width: 88px" />
          <col style="width: 48px" />
          <col />
        </colgroup>
        <thead><tr><th>时间</th><th>难度</th><th>模式</th><th>结果</th><th>奖杯</th><th>回合</th><th>核心干员</th></tr></thead>
        <tbody>
          {% for row in garrison.rows %}
          <tr>
            <td>{{ row.start }}</td>
            <td>{{ row.difficulty }}</td>
            <td>{{ row.mode }}</td>
            <td><span class="{{ 'g-win' if row.success else 'g-lose' }}">{{ '成功' if row.success else '失败' }}</span></td>
            <td>{{ row.trophy }}</td>
            <td>{{ row.rounds }}</td>
            <td title="{{ row.core_ops }}">{{ row.core_ops }}</td>
          </tr>
          {% endfor %}
        </tbody>
      </table>
      <div class="card-footer">数据来源：森空岛卫戍协议接口 · 共 {{ garrison.summary.total }} 条记录</div>
    </div>
  </body>
</html>
""",
    "garrison_trophy.html": """{% import "_macros.html" as ui %}
<!doctype html>
<html lang="zh-CN">
  <head>
    <meta charset="utf-8" />
    <style>
      {{ base_css | safe }}
      .t-name { font-size: 16px; font-weight: 700; }
      .t-sub { margin-top: 3px; font-size: 12px; color: var(--label); }
      .t-summary { margin-bottom: 14px; font-size: 14px; color: var(--label); }
      .t-table {
        width: 100%;
        table-layout: fixed;
        border-collapse: collapse;
        background: var(--panel-soft);
        font-size: 13px;
      }
      .t-table th, .t-table td {
        padding: 10px 8px;
        text-align: left;
        border-bottom: 1px solid var(--line-soft);
      }
      .t-table th { color: var(--label); font-weight: 600; background: var(--panel-alt); }
      .t-table tbody tr:nth-child(even) { background: rgba(255, 255, 255, 0.025); }
      .t-table tbody tr.t-own { background: rgba(245, 196, 81, 0.17); }
      .t-table .t-rank { width: 64px; color: var(--label); }
      .t-table .t-trophy { width: 110px; text-align: right; }
      .t-table td.t-trophy { font-size: 23px; font-weight: 700; color: #f5c451; }
      .t-table th, .t-table td, .t-name, .t-sub {
        white-space: nowrap;
        overflow: hidden;
        text-overflow: ellipsis;
      }
    </style>
  </head>
  <body>
    <div class="card t-garrison">
      {{ ui.card_header('卫戍奖杯排名', gt.summary) }}
      {% if gt.failed or gt.empty %}<div class="t-summary">{{ gt.skipped }}</div>{% endif %}
      <table class="t-table">
        <thead>
          <tr><th class="t-rank">名次</th><th>角色</th><th class="t-trophy">奖杯</th></tr>
        </thead>
        <tbody>
          {% for row in gt.rows %}
          <tr{% if row.own %} class="t-own"{% endif %}>
            <td class="t-rank">{{ row.rank }}</td>
            <td><div class="t-name">{{ row.name }}</div><div class="t-sub">uid {{ row.uid }} · {{ row.games }} 场记录</div></td>
            <td class="t-trophy">{{ row.trophy }}</td>
          </tr>
          {% endfor %}
        </tbody>
      </table>
      <p class="t-sub">数据来源：森空岛卫戍协议接口 · 取每个绑定角色历史记录中的最高奖杯</p>
    </div>
  </body>
</html>
""",
    "garrison_note.html": """{% import "_macros.html" as ui %}
<!doctype html>
<html lang="zh-CN">
  <head>
    <meta charset="utf-8" />
    <style>
      {{ base_css | safe }}
      .g-user {
        display: flex;
        align-items: center;
        gap: 12px;
        margin: -6px 0 16px;
        padding: 12px 16px;
        border: 1px solid var(--line);
        border-radius: 10px;
        background: var(--panel-alt);
      }
      .g-user .g-avatar {
        width: 44px;
        height: 44px;
        border-radius: 50%;
        border: 2px solid var(--line-strong);
        object-fit: cover;
        flex: none;
      }
      .g-user .g-name {
        font-size: 16px;
        font-weight: 700;
        color: var(--text);
      }
      .g-user .g-sub {
        font-size: 12px;
        color: var(--label);
        margin-top: 2px;
      }
      .g-user .g-assist {
        margin-left: auto;
        font-size: 12px;
        color: var(--label);
        display: flex;
        align-items: center;
        gap: 6px;
      }
      .g-user .g-assist img {
        width: 22px;
        height: 22px;
        border-radius: 50%;
      }
      .kpi {
        display: grid;
        grid-template-columns: 1fr 1fr 1fr;
        gap: 12px;
        margin-bottom: 16px;
      }
      .kpi .box {
        border: 1px solid var(--line);
        border-radius: 10px;
        padding: 14px 16px;
        background: var(--panel);
      }
      .kpi .k {
        font-size: 12px;
        color: var(--label);
        letter-spacing: 0.04em;
      }
      .kpi .v {
        font-size: 30px;
        font-weight: 800;
        margin-top: 6px;
        color: var(--theme);
        font-variant-numeric: tabular-nums;
      }
      .kpi .v small {
        font-size: 13px;
        font-weight: 600;
        color: var(--label);
        margin-left: 4px;
      }
      .sect {
        border: 1px solid var(--line);
        border-radius: 10px;
        padding: 14px 16px 8px;
        margin-bottom: 14px;
        background: var(--panel);
      }
      .sect h3 {
        margin: 0 0 10px;
        font-size: 14px;
        font-weight: 700;
        color: var(--text);
        display: flex;
        align-items: center;
        gap: 8px;
      }
      .sect h3::before {
        content: "";
        width: 4px;
        height: 14px;
        border-radius: 2px;
        background: var(--theme);
      }
      .row {
        display: grid;
        grid-template-columns: 120px 1fr 70px 54px;
        align-items: center;
        gap: 12px;
        padding: 9px 0;
        border-top: 1px solid var(--line-soft);
        font-size: 13px;
      }
      .row:first-of-type { border-top: 0; }
      .row .nm { color: var(--text); font-weight: 600; }
      .row .bar {
        height: 8px;
        border-radius: 4px;
        background: var(--line-soft);
        overflow: hidden;
      }
      .row .bar i {
        display: block;
        height: 100%;
        border-radius: 4px;
        background: linear-gradient(90deg, var(--theme), var(--theme-2));
      }
      .row .num {
        text-align: right;
        color: var(--label);
        font-variant-numeric: tabular-nums;
      }
      .row .num b { color: var(--text); font-weight: 700; }
      .row .rate {
        text-align: right;
        color: var(--theme);
        font-weight: 700;
        font-variant-numeric: tabular-nums;
      }
      .foot {
        display: flex;
        justify-content: space-between;
        gap: 16px;
        margin-top: 4px;
        padding-top: 10px;
        border-top: 1px solid var(--line);
        font-size: 12px;
        color: var(--label);
      }
      .foot .note { line-height: 1.6; }
    </style>
  </head>
  <body>
    <div class="card {{ card_class }}">
      {% set header_title %}卫戍便签{% endset %}{% set header_meta %}{{ gn.season_name }} · {{ gn.version }}{% endset %}
{{ ui.card_header(header_title, header_meta) }}
      <div class="g-user">
        {% if gn.user.avatar %}<img class="g-avatar" src="{{ gn.user.avatar }}" alt="" />{% endif %}
        <div>
          <div class="g-name">{{ gn.user.name or "未知" }}</div>
          <div class="g-sub">uid {{ gn.user.uid }} · Lv{{ gn.user.level }}</div>
        </div>
        {% if gn.user.secretary_name %}
          <div class="g-assist">
            {% if gn.user.secretary_icon %}<img src="{{ gn.user.secretary_icon }}" alt="" />{% endif %}
            助理 {{ gn.user.secretary_name }}
          </div>
        {% endif %}
      </div>
      <div class="kpi">
        {% set metric_value %}{{ gn.total }}{% endset %}{% set metric_unit %}场{% endset %}{{ ui.metric("总场数", metric_value, metric_unit, True, "box", "k", "v") }}
        {% set metric_value %}{{ gn.cleared }}{% endset %}{% set metric_unit %}次 · {{ gn.clear_rate }}%{% endset %}{{ ui.metric("通关", metric_value, metric_unit, True, "box", "k", "v") }}
        {% set metric_value %}{{ gn.trophy_now }}{% endset %}{% set metric_unit %}最高 {{ gn.trophy_best }}{% endset %}{{ ui.metric("奖杯", metric_value, metric_unit, True, "box", "k", "v") }}
      </div>
      <div class="sect">
        {{ ui.section("各难度通关") }}
        {% for item in gn.by_difficulty %}
          {{ ui.progress_row(item.name, item.cleared, item.total, item.rate) }}
        {% else %}
          <div class="empty">暂无记录</div>
        {% endfor %}
      </div>
      <div class="sect">
        {{ ui.section("模式分布") }}
        {% for item in gn.by_mode %}
          {{ ui.progress_row(item.name, item.cleared, item.total, item.rate) }}
        {% else %}
          <div class="empty">暂无记录</div>
        {% endfor %}
      </div>
      <div class="foot">
        <div class="note">
          累计击杀 {{ gn.kills }} · 累计花费 {{ gn.coins }} 金币<br />
          记录区间 {{ gn.span }}
        </div>
        <div class="note" style="text-align: right">
          数据来源：森空岛卫戍协议接口<br />
          共 {{ gn.total }} 条记录（接口提供的全部）
        </div>
      </div>
    </div>
  </body>
</html>
""",
    "garrison_recent.html": """{% import "_macros.html" as ui %}
<!doctype html>
<html lang="zh-CN">
  <head>
    <meta charset="utf-8" />
    <style>
      {{ base_css | safe }}
      /* ── user bar ─────────────────────────────── */
      .g-user {
        display: flex;
        align-items: center;
        gap: 12px;
        margin: -10px 0 18px;
        padding: 13px 16px;
        border: 1px solid var(--line);
        border-radius: 10px;
        background: var(--panel-alt);
      }
      .g-user .g-avatar {
        width: 44px;
        height: 44px;
        border-radius: 50%;
        border: 2px solid var(--line-strong);
        object-fit: cover;
        flex: none;
      }
      .g-user .g-who {
        min-width: 0;
      }
      .g-user .g-nm {
        font-size: 16px;
        font-weight: 700;
        color: var(--text);
      }
      .g-user .g-sub {
        font-size: 12px;
        color: var(--label);
        margin-top: 2px;
        white-space: nowrap;
        overflow: hidden;
        text-overflow: ellipsis;
      }
      .g-user .g-secy {
        margin-left: auto;
        display: flex;
        align-items: center;
        gap: 7px;
        padding: 5px 12px 5px 6px;
        border-radius: 18px;
        background: var(--panel-soft);
        border: 1px solid var(--line);
        flex: none;
      }
      .g-user .g-secy img {
        width: 24px;
        height: 24px;
        border-radius: 50%;
      }
      .g-user .g-secy .g-k {
        font-size: 12px;
        color: var(--muted);
      }
      .g-user .g-secy .g-v {
        font-size: 13px;
        color: var(--text);
        font-weight: 600;
      }
      /* ── one game card ─────────────────────────── */
      .g-game {
        display: flex;
        margin-bottom: 14px;
        border: 1px solid var(--line);
        border-radius: 12px;
        overflow: hidden;
        background: var(--panel-alt);
        box-shadow: 0 4px 16px rgba(0, 0, 0, 0.3);
      }
      .g-game:last-of-type {
        margin-bottom: 0;
      }
      .g-info {
        flex: 0 0 224px;
        padding: 18px 16px;
        display: flex;
        flex-direction: column;
        gap: 14px;
        background: linear-gradient(160deg, rgba(255, 255, 255, 0.03), transparent),
          var(--panel);
      }
      .g-badge {
        display: inline-block;
        align-self: flex-start;
        padding: 3px 13px;
        border-radius: 20px;
        font-size: 14px;
        font-weight: 700;
        color: #fff;
      }
      .g-badge.win {
        background: #2f9e6b;
      }
      .g-badge.lose {
        background: #b0483f;
      }
      .g-big {
        display: flex;
        align-items: baseline;
        gap: 7px;
      }
      .g-big .g-n {
        font-size: 46px;
        font-weight: 800;
        line-height: 1.5;
        color: var(--text);
        letter-spacing: -1px;
      }
      .g-big .g-t {
        font-size: 13px;
        color: var(--label);
      }
      /* Strategy icon and difficulty are separate elements. */
      .g-strat {
        display: flex;
        align-items: center;
        gap: 10px;
      }
      .g-strat img {
        width: 34px;
        height: 34px;
        border-radius: 8px;
        border: 1px solid var(--line);
      }
      .g-strat .g-snm {
        font-size: 17px;
        font-weight: 700;
        color: var(--text);
      }
      .g-diff {
        display: flex;
        align-items: center;
        gap: 7px;
        padding-left: 4px;
      }
      .g-diff .g-dic {
        font-size: 13px;
        color: var(--muted);
      }
      .g-diff .g-dnm {
        font-size: 15px;
        color: var(--label);
        font-weight: 600;
      }
      .g-meta {
        display: flex;
        flex-direction: column;
        gap: 8px;
      }
      .g-meta .g-line {
        display: flex;
        align-items: center;
        gap: 7px;
        font-size: 12px;
        color: var(--label);
      }
      .g-meta .g-line .g-ic {
        width: 16px;
        text-align: center;
        opacity: 0.75;
      }
      /* ── right column ──────────────────────────── */
      .g-right {
        flex: 1;
        display: flex;
        flex-direction: column;
        min-width: 0;
      }
      .g-board {
        padding: 14px 14px 12px;
        display: flex;
        flex-direction: column;
        justify-content: center;
        gap: 8px;
        flex: 1;
      }
      .g-grid {
        display: grid;
        grid-template-columns: repeat(5, 1fr);
        gap: 8px;
      }
      .g-cell {
        position: relative;
        aspect-ratio: 1;
        border-radius: 7px;
        overflow: hidden;
        background: var(--panel);
        border: 1px solid var(--line);
      }
      .g-cell img.g-face {
        width: 100%;
        height: 100%;
        object-fit: cover;
      }
      .g-cell .g-rom {
        position: absolute;
        top: 2px;
        left: 2px;
        padding: 0 4px;
        border-radius: 3px;
        background: rgba(0, 0, 0, 0.72);
        font-size: 12px;
        font-weight: 700;
        color: #ffd479;
        line-height: 18px;
      }
      .g-cell .g-eqs {
        position: absolute;
        left: 2px;
        right: 2px;
        bottom: 2px;
        display: flex;
        gap: 2px;
      }
      .g-cell .g-eqs img {
        width: 14px;
        height: 14px;
        border-radius: 3px;
        border: 1px solid rgba(255, 255, 255, 0.25);
      }
      .g-bonds {
        padding: 12px 14px;
        border-top: 1px solid var(--line-soft);
      }
      .g-bonds h3 {
        font-size: 12px;
        color: var(--muted);
        font-weight: 600;
        margin-bottom: 8px;
      }
      .g-bonds .g-blist {
        display: flex;
        flex-wrap: wrap;
        gap: 7px;
      }
      .g-bond {
        display: flex;
        align-items: center;
        gap: 6px;
        padding: 4px 11px 4px 5px;
        border-radius: 18px;
        background: var(--panel-soft);
        border: 1px solid var(--line);
      }
      .g-bond.off {
        opacity: 0.45;
      }
      .g-bond img {
        width: 20px;
        height: 20px;
        border-radius: 50%;
      }
      .g-bond .g-bnm {
        font-size: 12px;
        color: var(--text);
      }
      .g-bond .g-blv {
        font-size: 12px;
        color: var(--accent-2);
        font-weight: 600;
      }
      .g-foot {
        display: flex;
        align-items: center;
        justify-content: space-between;
        padding: 9px 14px;
        font-size: 12px;
        color: var(--muted);
        border-top: 1px solid var(--line-soft);
        background: var(--panel);
      }
    </style>
  </head>
  <body>
    <div class="card {{ card_class }}">
      {% if garrison.user %}
      {% call ui.card_header("") %}<div class="g-user">
        {% if garrison.user.avatar %}
        <img class="g-avatar" src="{{ garrison.user.avatar }}" alt="" />
        {% endif %}
        <div class="g-who">
          <div class="g-nm">{{ garrison.user.name or '—' }}</div>
          <div class="g-sub">
            uid {{ garrison.user.uid }} · Lv{{ garrison.user.level }} ·
            {{ garrison.season_name }} · {{ garrison.version }} · {{ garrison.phase_name }}
          </div>
        </div>
        {% if garrison.user.secretary_name %}
        <div class="g-secy">
          {% if garrison.user.secretary_icon %}
          <img src="{{ garrison.user.secretary_icon }}" alt="" />
          {% endif %}
          <span class="g-k">助理</span>
          <span class="g-v">{{ garrison.user.secretary_name }}</span>
        </div>
        {% endif %}
      </div>
{% endcall %}
      {% endif %}
      {% for r in garrison.records %}
      <div class="g-game">
        <div class="g-info">
          <span class="g-badge {{ 'win' if r.success else 'lose' }}">{{ r.title }}</span>
          <div class="g-big">
            <span class="g-n">{{ r.pass_round }}</span>
            <span class="g-t">{{ r.mode }}</span>
          </div>
          <div class="g-strat">
            {% if r.band_icon %}<img src="{{ r.band_icon }}" alt="" />{% endif %}
            <span class="g-snm">{{ r.strategy_name or '—' }}</span>
          </div>
          <div class="g-diff">
            <span class="g-dic">◆</span>
            <span class="g-dnm">{{ r.difficulty }}</span>
          </div>
          <div class="g-meta">
            <div class="g-line"><span class="g-ic">◔</span><span>{{ r.start }}</span></div>
            <div class="g-line"><span class="g-ic">⏱</span><span>{{ r.duration }}</span></div>
          </div>
        </div>
        <div class="g-right">
          <div class="g-board">
            <div class="g-grid">
              {% for u in r.squad %}
              <div class="g-cell">
                {% if u.avatar %}<img class="g-face" src="{{ u.avatar }}" alt="" />{% endif %}
                <span class="g-rom">{{ u.roman }}</span>
                {% if u.equips %}
                <div class="g-eqs">
                  {% for e in u.equips %}{% if e.icon %}<img src="{{ e.icon }}" alt="" />{% endif %}{% endfor %}
                </div>
                {% endif %}
              </div>
              {% endfor %}
            </div>
          </div>
          {% if r.bonds %}
          <div class="g-bonds">
            {{ ui.section("核心盟约") }}
            <div class="g-blist">
              {% for b in r.bonds %}
              <div class="g-bond {{ '' if b.activate else 'off' }}">
                {% if b.icon %}<img src="{{ b.icon }}" alt="" />{% endif %}
                <span class="g-bnm">{{ b.name }}</span>
                <span class="g-blv">Lv{{ b.layer }}</span>
              </div>
              {% endfor %}
            </div>
          </div>
          {% endif %}
          <div class="g-foot">
            <span>奖杯 {{ r.trophy_before }}→{{ r.trophy_after }}</span>
            <span>击杀 {{ r.kill_cnt }} · 金币 {{ r.coin_cost }}</span>
          </div>
        </div>
      </div>
      {% endfor %}
    </div>
  </body>
</html>
""",
    "help.html": """{% import "_macros.html" as ui %}
<!doctype html>
<html lang="zh-CN">
  <head>
    <meta charset="utf-8" />
    <style>
      {{ base_css | safe }}
      .help-group {
        break-inside: avoid;
      }
    </style>
  </head>
  <body>
    <div class="card {{ card_class }}">
      {% set header_title %}罗德岛终端{% endset %}{% set header_meta %}Rhodes Island · v{{ version }}{% endset %}
{{ ui.card_header(header_title, header_meta) }}
      {% for section in sections %}
      <div class="panel">
        {% set section_title %}{{ section.title }}{% endset %}{{ ui.section(section_title) }}
        <div class="help-grid">
          {% for item in section["items"] %}
          <div class="help-group">
            <div class="help-command">{{ item.cmd }}</div>
            <div class="help-desc">{{ item.desc }}</div>
          </div>
          {% endfor %}
        </div>
      </div>
      {% endfor %}
      <div class="card-footer">
        <span>© HYPERGRYPH · 账号凭证仅保存在本机，不会在任何回复中回显</span>
        <span><span class="barcode"></span><span class="serial">RI-TERMINAL-001</span></span>
      </div>
    </div>
  </body>
</html>
""",
    "note.html": """{% import "_macros.html" as ui %}
{% from "training_badges.html" import training %}
<!doctype html>
<html lang="zh-CN">
  <head>
    <meta charset="utf-8" />
    <style>
      {{ base_css | safe }}
      .id-block {
        display: flex;
        align-items: flex-end;
        justify-content: space-between;
        width: 100%;
      }
      .id-name {
        font-size: 34px;
        font-weight: 800;
        letter-spacing: 0.8px;
      }
      .id-level {
        font-size: 12px;
        color: var(--label);
        letter-spacing: 1.6px;
      }
      .id-level b {
        color: var(--theme);
        font-size: 26px;
        margin-left: 7px;
      }
      .body {
        display: flex;
        gap: 22px;
        align-items: stretch;
      }
      /* Assistant column: the artwork fills the whole column height and the
         badge strip sits underneath, as in the approved design. */
      .assistant {
        width: 316px;
        flex: none;
        display: flex;
        flex-direction: column;
      }
      .assistant-art {
        position: relative;
        flex: 1;
        min-height: 430px;
        border: 1px solid var(--line);
        border-radius: 8px 8px 0 0;
        background:
          linear-gradient(145deg, rgba(255, 130, 159, 0.22), transparent 42%),
          linear-gradient(25deg, rgba(98, 219, 233, 0.18), transparent 48%),
          linear-gradient(180deg, #222638 0%, #0e1119 100%);
        overflow: hidden;
      }
      .assistant-art::before {
        content: "";
        position: absolute;
        inset: 0;
        z-index: 1;
        background: linear-gradient(180deg, transparent 68%, rgba(8, 10, 17, 0.38));
        pointer-events: none;
      }
      .assistant-art img {
        position: absolute;
        inset: 0;
        width: 100%;
        height: 100%;
        box-sizing: border-box;
        padding: 12px 6px;
        object-fit: cover;
        object-position: center top;
        display: block;
        filter: saturate(1.1) contrast(1.02);
      }
      .assistant-badge {
        display: flex;
        align-items: center;
        gap: 10px;
        border: 1px solid var(--line);
        border-top: none;
        padding: 9px 12px;
        border-radius: 0 0 8px 8px;
        background: linear-gradient(90deg, rgba(255, 130, 159, 0.14), rgba(20, 23, 35, 0.95));
      }
      .assistant-badge .cls {
        width: 30px;
        height: 30px;
        flex: none;
      }
      .assistant-badge .rank {
        height: 17px;
        flex: none;
      }
      .assistant-name {
        font-size: 17px;
        font-weight: 700;
        letter-spacing: 0.5px;
      }
      .assistant-role {
        font-size: 12px;
        color: var(--muted);
        letter-spacing: 1.8px;
        margin-top: 1px;
      }
      .signature {
        margin-top: 9px;
        padding: 9px 11px;
        border: 1px solid var(--line);
        border-left: 2px solid var(--theme-2);
        border-radius: 6px;
        background: rgba(20, 22, 33, 0.86);
        font-size: 12px;
        color: var(--label);
        line-height: 1.55;
        max-height: 76px;
        overflow: hidden;
      }
      .right {
        flex: 1;
        min-width: 0;
      }
      .stat-strip {
        display: flex;
        margin-bottom: 14px;
        border: 1px solid var(--line);
        border-radius: 7px;
        overflow: hidden;
        background: rgba(13, 15, 24, 0.66);
      }
      .stat-cell {
        flex: 1;
        padding: 10px 13px;
        border-right: 1px solid var(--line);
      }
      .stat-cell:last-child {
        border-right: none;
      }
      .stat-key {
        font-size: 12px;
        color: var(--muted);
        letter-spacing: 1.4px;
      }
      .stat-val {
        font-size: 21px;
        font-weight: 800;
        margin-top: 4px;
      }
      .pct {
        display: block;
        font-size: 16px;
        font-weight: 600;
        color: var(--muted);
        margin-top: 2px;
        white-space: nowrap;
      }
      .assist-op {
        width: 104px;
      }
      .assist-op img {
        width: 98px;
        height: 98px;
        border-color: color-mix(in srgb, var(--theme-2) 34%, var(--line));
      }
      .assist-op .name {
        font-size: 12px;
        color: var(--text);
      }
      .assist-op .lv {
        font-size: 12px;
        color: var(--muted);
        letter-spacing: 0.5px;
      }
      .serial {
        letter-spacing: 1.2px;
      }
      .training { font-size: 12px; line-height: 1.6; overflow-wrap: anywhere; color: var(--muted); padding: 5px; }
      {% include "training_badges.css" %}
    </style>
  </head>
  <body>
    <div class="card {{ card_class }}">
      {% set header_title %}{{ note.nickname or "未知博士" }}<div style="font-size:12px;color:var(--muted);margin-top:5px">UID {{ note.uid }}</div>{% endset %}
{% set header_meta %}<span class="id-level">LEVEL<b>{{ note.level }}</b></span>{% endset %}
{{ ui.card_header(header_title, header_meta) }}
      <div class="training-legend hint">技能下方亮菱形 = 专精等级（0–3） · 模组六边形 I / II / III = 等级</div>
      <div class="body">
        <div class="assistant rarity-{{ note.secretary.stars }}">
          <div class="assistant-art">
            {% if note.secretary.portrait %}
            <img src="{{ note.secretary.portrait }}" alt="{{ note.secretary.name }}" />
            {% endif %}
            <span class="tick"></span>
            {% if note.secretary.artwork_name %}<span style="position:absolute;bottom:8px;right:8px;z-index:2;font-size:12px;color:var(--muted);background:#101521bb;padding:3px 6px;border-radius:3px">{{ note.secretary.artwork_name }}</span>{% endif %}
          </div>
          <div class="assistant-badge">
            {% if note.secretary.profession_icon %}
            <img class="cls" src="{{ note.secretary.profession_icon }}" alt="" />
            {% endif %}
            <span>
              <span class="assistant-name">{{ note.secretary.name or "未设置助理" }}</span>
              <span class="assistant-role">ASSISTANT</span>
            </span>
            {% if note.secretary.rarity_icon %}
            <img class="rank" src="{{ note.secretary.rarity_icon }}" alt="" style="margin-left: auto" />
            {% endif %}
          </div>
          {{ training(note.secretary) }}
          {% if note.signature %}
          <div class="signature">{{ note.signature }}</div>
          {% endif %}
        </div>
        <div class="right">
          <div class="stat-strip">
            {% set metric_label %}入职日期{% endset %}{% set metric_value %}{{ note.register_date }}{% endset %}{{ ui.metric(metric_label, metric_value, classes="stat-cell", label_class="stat-key", value_class="stat-val") }}
            {% set metric_label %}主线进度{% endset %}{% set metric_value %}{{ note.main_stage }}{% endset %}{{ ui.metric(metric_label, metric_value, classes="stat-cell", label_class="stat-key", value_class="stat-val") }}
          </div>
          <div class="stat-strip">
            {% set metric_label %}干员数量{% endset %}{% set metric_value %}{{ note.roster.owned }} / {{ note.roster.total }}<span class="pct">{{ "%.1f" | format(note.roster.owned_percent) }}%</span>{% endset %}{{ ui.metric(metric_label, metric_value, classes="stat-cell", label_class="stat-key", value_class="stat-val") }}
            {% set metric_label %}时装数量{% endset %}{% set metric_value %}{{ note.skin_count }}{% endset %}{{ ui.metric(metric_label, metric_value, classes="stat-cell", label_class="stat-key", value_class="stat-val") }}
          </div>
          <div class="progress" style="margin: 2px 0 12px; width: calc(50% - 6px);">
            <div class="progress-fill" style="width: {{ note.roster.owned_percent }}%"></div>
          </div>
          <div class="stat-strip">
            {% set metric_label %}精二干员总数{% endset %}{% set metric_value %}{{ note.elite2_count }}{% endset %}{{ ui.metric(metric_label, metric_value, classes="stat-cell", label_class="stat-key", value_class="stat-val") }}
            {% set metric_label %}专三技能总数{% endset %}{% set metric_value %}{{ note.mastery3_count }}{% endset %}{{ ui.metric(metric_label, metric_value, classes="stat-cell", label_class="stat-key", value_class="stat-val") }}
          </div>
          <div class="stat-strip">
            {% set metric_label %}总收集模组{% endset %}{% set metric_value %}{{ note.module_count }}{% endset %}{{ ui.metric(metric_label, metric_value, classes="stat-cell", label_class="stat-key", value_class="stat-val") }}
            {% set metric_label %}STAGE 3 模组{% endset %}{% set metric_value %}{{ note.module_stage3_count }}{% endset %}{{ ui.metric(metric_label, metric_value, classes="stat-cell", label_class="stat-key", value_class="stat-val") }}
            {% set metric_label %}拥有模组干员{% endset %}{% set metric_value %}{{ note.module_operator_count }}{% endset %}{{ ui.metric(metric_label, metric_value, classes="stat-cell", label_class="stat-key", value_class="stat-val") }}
          </div>
          <div class="panel">
            {% set section_title %}理智{% endset %}{{ ui.section(section_title) }}
            <div class="row">
              <span class="row-label">当前理智</span>
              <span class="row-value accent">
                {{ note.sanity.current }}
                <span style="color: var(--muted); font-weight: 400">
                  / {{ note.sanity.max }}
                </span>
              </span>
            </div>
            <div class="progress">
              <div class="progress-fill" style="width: {{ note.sanity.percent }}%"></div>
            </div>
            <div class="row">
              <span class="row-label">恢复</span>
              <span class="row-value">{{ note.sanity.remaining_text }}</span>
            </div>
          </div>
          <div class="panel">
            {% set section_title %}进度{% endset %}{{ ui.section(section_title) }}
            {% for item in [{"label": "每日任务", "node": note.daily},
                            {"label": "每周任务", "node": note.weekly},
                            {"label": "剿灭合成玉", "node": note.campaign}] %}
            <div class="row">
              <span class="row-label">{{ item.label }}</span>
              <span class="row-value">{{ item.node.current }} / {{ item.node.total }}</span>
            </div>
            <div class="progress">
              <div class="progress-fill" style="width: {{ item.node.percent }}%"></div>
            </div>
            {% endfor %}
          </div>
          <div class="panel" style="margin-bottom: 0">
            {% set section_title %}助战干员{% endset %}{{ ui.section(section_title) }}
            {% if note.assist %}
            <div class="grid">
              {% for op in note.assist %}
              <div class="tile assist-op rarity-{{ op.stars }}" data-rarity="{{ op.stars }}">
                <img src="{{ op.avatar }}" alt="{{ op.name }}" />
                <div class="name">{{ op.name }}</div>
                {{ training(op) }}
                <div class="lv">Lv.{{ op.level }}</div>
              </div>
              {% endfor %}
            </div>
            {% else %}
            <div class="empty">未设置助战干员</div>
            {% endif %}
          </div>
        </div>
      </div>
      <div class="card-footer">
        <span>© HYPERGRYPH · 数据时间 {{ note.data_time }}</span>
        <span>
          <span class="barcode"></span>
          <span class="serial">
            RI-{{ note.register_date | replace("-", "") }}-{{ note.level }}
          </span>
        </span>
      </div>
    </div>
  </body>
</html>
""",
    "operator.html": """{% import "_macros.html" as ui %}
<!doctype html>
<html lang="zh-CN">
  <head>
    <meta charset="utf-8" />
    <style>
      {{ base_css | safe }}
      .detail {
        display: flex;
        gap: 24px;
        align-items: flex-start;
      }
      .detail-portrait {
        width: 320px;
        flex: none;
        position: relative;
        overflow: hidden;
        border: 1px solid var(--line);
        border-radius: 8px;
        background:
          linear-gradient(145deg, rgba(255, 202, 98, 0.2), transparent 40%),
          linear-gradient(25deg, rgba(255, 113, 143, 0.18), transparent 45%),
          #151925;
      }
      .detail-portrait img {
        width: 320px;
        height: 456px;
        object-fit: contain;
        object-position: center bottom;
        display: block;
        filter: saturate(1.08) contrast(1.02);
      }
      .detail-portrait::after {
        content: "";
        position: absolute;
        bottom: 0;
        left: 0;
        width: 92px;
        height: 6px;
        background: linear-gradient(90deg, var(--theme), var(--theme-2));
      }
      .detail-body {
        flex: 1;
        min-width: 0;
      }
      .detail-name {
        font-size: 36px;
        font-weight: 800;
        letter-spacing: 1px;
        line-height: 1.5;
      }
      .detail-name::before {
        content: "";
        display: inline-block;
        width: 6px;
        height: 28px;
        margin-right: 12px;
        background: linear-gradient(180deg, var(--theme), var(--theme-2));
        vertical-align: -2px;
      }
      .detail-meta {
        display: flex;
        align-items: center;
        gap: 10px;
        margin: 12px 0 20px;
        flex-wrap: wrap;
      }
      .detail-meta img.rank {
        height: 17px;
      }
      .detail-meta img.cls {
        width: 26px;
        height: 26px;
      }
      .detail-meta img.mark {
        height: 20px;
      }
      .badge {
        font-size: 12px;
        letter-spacing: 1.4px;
        padding: 3px 11px;
        border: 1px solid var(--line);
        color: var(--label);
      }
      .badge.hot {
        border-color: var(--theme);
        color: var(--theme);
      }
      .skill-row {
        display: flex;
        align-items: center;
        gap: 11px;
        padding: 8px 0;
        border-bottom: 1px solid var(--line-soft);
        font-size: 14px;
      }
      .skill-row:last-child {
        border-bottom: none;
      }
      .skill-row img {
        width: 42px;
        height: 42px;
        border: 1px solid var(--line);
        border-radius: 6px;
        background: var(--panel-alt);
        flex: none;
      }
      .skill-name {
        flex: 1;
        color: var(--label);
        font-family: Menlo, Consolas, monospace;
        font-size: 12px;
        overflow: hidden;
        text-overflow: ellipsis;
      }
      .mark {
        font-size: 12px;
        letter-spacing: 1px;
        color: #0a0b0d;
        background: var(--theme);
        padding: 1px 5px;
      }
    </style>
  </head>
  <body>
    <div class="card {{ card_class }}">
      <div class="detail rarity-{{ op.stars }}">
        <div class="detail-portrait">
          <img src="{{ op.portrait or op.avatar }}" alt="{{ op.name }}" />
        </div>
        <div class="detail-body">
          {{ ui.card_header(op.name) }}
          <div class="detail-meta">
            {% if op.rarity_icon %}
            <img class="rank" src="{{ op.rarity_icon }}" alt="{{ op.stars }}星" />
            {% else %}
            <span class="stars">{{ "★" * op.stars }}</span>
            {% endif %}
            {% if op.profession_icon %}
            <img class="cls" src="{{ op.profession_icon }}" alt="{{ op.profession_cn }}" />
            {% endif %}
            <span class="badge">{{ op.profession_cn }}</span>
            {% if op.elite_icon and op.elite %}
            <img class="mark" src="{{ op.elite_icon }}" alt="精英{{ op.elite }}" />
            {% elif not op.elite %}
            <span class="badge">未精英化</span>
            {% endif %}
            <span style="font-size:12px;color:var(--muted)">潜能 {{ op.potential + 1 }}</span>
            {% if op.potential_icon %}
            <img class="mark" src="{{ op.potential_icon }}" alt="潜能{{ op.potential + 1 }}" />
            {% endif %}
            <span class="badge hot">信赖 {{ op.favor }}%</span>
          </div>
          <div class="panel">
            {% set section_title %}培养{% endset %}{{ ui.section(section_title) }}
            <div class="row">
              <span class="row-label">等级</span>
              <span class="row-value accent">{{ op.level }}</span>
            </div>
            <div class="progress">
              <div class="progress-fill" style="width: {{ op.favor_percent }}%"></div>
            </div>
          </div>
          <div class="panel">
            {% set section_title %}技能{% endset %}{{ ui.section(section_title) }}
            {% if op.skills %}
            {% for skill in op.skills %}
            <div class="skill-row">
              {% if skill.icon %}<img src="{{ skill.icon }}" alt="{{ skill.id }}" />{% endif %}
              <span class="skill-name">{{ skill.id }}</span>
              {% if skill.is_default %}<span class="mark">默认</span>{% endif %}
              <span class="row-value">
                {% if skill.specialize %}专精 {{ skill.specialize }}{% else %}未专精{% endif %}
              </span>
            </div>
            {% endfor %}
            {% else %}
            <div class="empty">暂无技能数据</div>
            {% endif %}
          </div>
          <div class="panel">
            {% set section_title %}模组{% endset %}{{ ui.section(section_title) }}
            {% if op.equips %}
            {% for equip in op.equips %}
            <div class="row">
              <span class="row-label">{{ equip.name }}</span>
              <span class="row-value">Lv.{{ equip.level }}</span>
            </div>
            {% endfor %}
            {% else %}
            <div class="empty">未装配模组</div>
            {% endif %}
          </div>
        </div>
      </div>
      <div class="card-footer">
        <span>© HYPERGRYPH · SNAPSHOT / SKLAND</span>
        <span><span class="barcode"></span><span class="serial">RI-OPERATOR-001</span></span>
      </div>
    </div>
  </body>
</html>
""",
    "operator_list.html": """{% import "_macros.html" as ui %}
{% from "training_badges.html" import training %}
<!doctype html>
<html lang="zh-CN">
  <head>
    <meta charset="utf-8" />
    <style>
      {{ base_css | safe }}
      .roster-group {
        margin-bottom: 20px;
        padding: 12px 14px 14px;
        border: 1px solid var(--line);
        border-radius: 7px;
        background: rgba(13, 15, 24, 0.58);
      }
      .roster-head {
        display: flex;
        align-items: center;
        gap: 9px;
        margin-bottom: 9px;
        padding-bottom: 5px;
        border-bottom: 1px solid var(--line-soft);
      }
      .roster-head img {
        width: 20px;
        height: 20px;
        flex: none;
    }
      .roster-name {
        font-size: 13px;
        font-weight: 700;
        color: var(--theme);
        letter-spacing: 2px;
      }
      .roster-count {
        font-size: 12px;
        color: var(--muted);
        border: 1px solid var(--line);
        padding: 0 6px;
        line-height: 18px;
      }
      .tile {
        position: relative;
        width: 110px;
      }
      .tile img {
        width: 70px;
        height: 70px;
      }
      .tile .stars {
        font-size: 12px;
        color: var(--theme);
        text-align: center;
        line-height: 18px;
        letter-spacing: 0;
      }
      .tile .elite {
        position: absolute;
        top: 0;
        left: 0;
        font-size: 12px;
        font-weight: 700;
        color: #0a0b0d;
        background: linear-gradient(135deg, var(--theme), var(--theme-2));
        padding: 0 4px;
      }
      .training { font-size: 12px; line-height: 1.5; overflow-wrap: anywhere; color: var(--muted); margin-top: 4px; }
      {% include "training_badges.css" %}
    </style>
  </head>
  <body>
    <div class="card {{ card_class }}">
      {% set header_title %}干员列表{% endset %}{% set header_meta %}已收集 {{ roster.owned }} / 全干员 {{ roster.total }}（{{ "%.1f" | format(roster.owned_percent) }}%）{% endset %}{{ ui.card_header(header_title, header_meta) }}
      <div class="training-legend hint">技能下方亮菱形 = 专精等级（0–3） · 模组六边形 I / II / III = 等级</div>
      <div class="progress">
        <div class="progress-fill" style="width: {{ roster.owned_percent }}%"></div>
      </div>
      {% if roster.groups %}
      {% for group in roster.groups %}
      <div class="roster-group">
        <div class="roster-head">
          {% if group.operators[0].profession_icon %}
          <img src="{{ group.operators[0].profession_icon }}" alt="" />
          {% endif %}
          {{ ui.section(group.profession_cn) }}
          <span class="roster-count">{{ group.operators | length }}</span>
        </div>
        <div class="grid">
          {% for op in group.operators %}
          <div class="tile rarity-{{ op.stars }}" data-rarity="{{ op.stars }}">
            <img src="{{ op.avatar }}" alt="{{ op.name }}" />
            {% if op.elite %}<span class="elite">E{{ op.elite }}</span>{% endif %}
            <div class="stars">{{ "★" * op.stars }}</div>
            <div class="name">{{ op.name }}</div>
            {{ training(op) }}
          </div>
          {% endfor %}
        </div>
      </div>
      {% endfor %}
      {% else %}
      <div class="empty">没有查询到已持有的干员。</div>
      {% endif %}
      <div class="card-footer">
        <span>© HYPERGRYPH · E1 / E2 为精英化阶段，星级为干员稀有度<br />总数来自 PRTS 干员一览，每日自动更新</span>
        <span><span class="barcode"></span><span class="serial">RI-ROSTER-001</span></span>
      </div>
    </div>
  </body>
</html>
""",
    "recruit.html": """{% import "_macros.html" as ui %}
<!doctype html>
<html lang="zh-CN">
  <head>
    <meta charset="utf-8" />
    <style>
      {{ base_css | safe }}
      .summary {
        display: flex;
        border: 1px solid var(--line);
        margin-bottom: 20px;
      }
      .summary-cell {
        flex: 1;
        padding: 10px 14px;
        border-right: 1px solid var(--line);
      }
      .summary-cell:last-child {
        border-right: none;
      }
      .summary-key {
        font-size: 12px;
        color: var(--muted);
        letter-spacing: 1.3px;
      }
      .summary-val {
        font-size: 20px;
        font-weight: 700;
        margin-top: 4px;
      }
      .slot-grid {
        display: grid;
        grid-template-columns: 1fr 1fr;
        gap: 12px;
      }
      .slot-card {
        border: 1px solid var(--line);
        padding: 13px 15px;
        position: relative;
      }
      .slot-card.running {
        border-color: var(--accent);
      }
      .slot-index {
        font-size: 12px;
        color: var(--muted);
        letter-spacing: 1.4px;
      }
      .slot-state {
        font-size: 18px;
        font-weight: 700;
        margin-top: 6px;
      }
      .slot-card.running .slot-state {
        color: var(--accent);
      }
      .slot-card.done .slot-state {
        color: var(--accent);
      }
      .slot-time {
        font-size: 12px;
        color: var(--label);
        margin-top: 5px;
      }
      .slot-bar {
        position: absolute;
        top: 0;
        left: 0;
        width: 4px;
        height: 100%;
        background: var(--line);
      }
      .slot-card.running .slot-bar,
      .slot-card.done .slot-bar {
        background: var(--accent);
      }
    </style>
  </head>
  <body>
    <div class="card {{ card_class }}">
      {% set header_title %}公开招募{% endset %}{% set header_meta %}Recruitment{% endset %}
{{ ui.card_header(header_title, header_meta) }}
      <div class="summary">
        <div class="summary-cell">
          <div class="summary-key">栏位</div>
          <div class="summary-val">{{ recruit.slots | length }}</div>
        </div>
        <div class="summary-cell">
          <div class="summary-key">招募中</div>
          <div class="summary-val">{{ recruit.running }}</div>
        </div>
        <div class="summary-cell">
          <div class="summary-key">可领取</div>
          <div class="summary-val">{{ recruit.ready }}</div>
        </div>
      </div>
      {% if recruit.slots %}
      <div class="slot-grid">
        {% for slot in recruit.slots %}
        <div class="slot-card {{ slot.state }}">
          <div class="slot-bar"></div>
          <div class="slot-index">SLOT {{ slot.index }}</div>
          <div class="slot-state">{{ slot.state_cn }}</div>
          <div class="slot-time">{{ slot.remaining_text or "—" }}</div>
        </div>
        {% endfor %}
      </div>
      {% else %}
      <div class="empty">没有读取到公开招募栏位</div>
      {% endif %}
      <div class="card-footer">
        <span>© HYPERGRYPH · 森空岛接口只返回栏位状态，不返回公招词条</span>
        <span><span class="barcode"></span><span class="serial">RI-RECRUIT-001</span></span>
      </div>
    </div>
  </body>
</html>
""",
    "rogue.html": """{% import "_macros.html" as ui %}
<!doctype html>
<html lang="zh-CN">
  <head>
    <meta charset="utf-8" />
    <style>
      {{ base_css | safe }}
      .theme {
        border: 1px solid var(--line);
        margin-bottom: 12px;
      }
      .theme-head {
        display: flex;
        align-items: center;
        justify-content: space-between;
        padding: 10px 14px;
        background: var(--panel-alt);
        border-bottom: 1px solid var(--line);
      }
      .difficulty-details { padding: 12px 14px; border-top: 1px solid var(--line-soft); font-size: 12px; line-height: 1.8; }
      .difficulty-details strong { color: var(--accent); }
      .difficulty-note { color: var(--muted); font-size: 12px; }
      .theme-name {
        font-size: 15px;
        font-weight: 600;
        letter-spacing: 0.6px;
      }
      .theme-name::before {
        content: "";
        display: inline-block;
        width: 4px;
        height: 14px;
        margin-right: 9px;
        background: var(--accent);
        vertical-align: -2px;
      }
      .theme-body {
        display: grid;
        grid-template-columns: repeat(6, 1fr);
      }
      .theme-stat {
        grid-column: span 2;
        padding: 11px 14px;
        border-right: 1px solid var(--line-soft);
      }
      .theme-stat-wide { grid-column: span 3; }
      .theme-stat-summary { border-bottom: 1px solid var(--line-soft); }
      .theme-stat-row-end {
        border-right: none;
      }
      .theme-key {
        font-size: 12px;
        color: var(--muted);
        letter-spacing: 1.3px;
      }
      .theme-val {
        font-size: 21px;
        font-weight: 700;
        margin-top: 3px;
      }
      .theme-val.accent {
        color: var(--accent);
      }
    </style>
  </head>
  <body>
    <div class="card {{ card_class }}">
      {% set header_title %}集成战略{% endset %}{% set header_meta %}Integrated Strategies{% endset %}
{{ ui.card_header(header_title, header_meta) }}
      {% if rogue.themes %}
      {% for theme in rogue.themes %}
      <div class="theme">
        <div class="theme-head">
          {{ ui.section(theme.name) }}
        </div>
        <div class="theme-body">
          <div class="theme-stat theme-stat-wide theme-stat-summary"><div class="theme-key">历史最高分</div><div class="theme-val accent">{{ theme.highest_score if theme.highest_score is not none else "未提供" }}</div></div>
          <div class="theme-stat theme-stat-wide theme-stat-summary theme-stat-row-end"><div class="theme-key">当前等级</div><div class="theme-val accent">{{ theme.level if theme.level is not none else "未提供" }}</div></div>
          <div class="theme-stat"><div class="theme-key">累计节点</div><div class="theme-val accent">{{ theme.nodes if theme.nodes is not none else "未提供" }}</div></div>
          <div class="theme-stat"><div class="theme-key">通关次数</div><div class="theme-val">{{ theme.clears if theme.clears is not none else "未提供" }}</div></div>
          <div class="theme-stat theme-stat-row-end">
            <div class="theme-key">收藏品</div>
            <div class="theme-val accent">{{ theme.relics }}</div>
          </div>
          <div class="theme-stat theme-stat-wide">
            <div class="theme-key">投资系统</div>
            <div class="theme-val">{{ theme.bank }}</div>
          </div>
          <div class="theme-stat theme-stat-wide theme-stat-row-end">
            <div class="theme-key">投资历史最高</div>
            <div class="theme-val">{{ theme.bank_record }}</div>
          </div>
        </div>
        <div class="difficulty-details">
          <strong>最高通关难度：{{ theme.highest_difficulty or "未提供" }}{% if theme.highest_difficulty and theme.highest_from_history %}（历史对局最高）{% endif %}</strong>
          {% if theme.ending_difficulties %}<div>{{ theme.ending_difficulties | join("　·　") }}</div>{% endif %}
          {% if theme.highest_from_history %}<div class="difficulty-note hint">接口没有该主题的通关难度记录，这里取历史对局最高难度</div>{% elif not theme.ending_details_complete %}<div class="difficulty-note hint">接口未提供各结局完整的最高难度记录</div>{% endif %}
        </div>
      </div>
      {% endfor %}
      {% else %}
      <div class="empty">暂无集成战略记录</div>
      {% endif %}
      <div class="card-footer">
        <span>© HYPERGRYPH · 累计节点来自主题生涯统计 · 通关次数来自森空岛快照 · 未提供不代表零 · 分数与等级来自森空岛主题生涯接口，未提供不代表零</span>
        <span><span class="barcode"></span><span class="serial">RI-ROGUE-001</span></span>
      </div>
    </div>
  </body>
</html>
""",
    "sanity.html": """{% import "_macros.html" as ui %}
<!doctype html>
<html lang="zh-CN">
  <head>
    <meta charset="utf-8" />
    <style>
      {{ base_css | safe }}
      .sanity-block {
        display: flex;
        align-items: baseline;
        gap: 14px;
        margin: 2px 0 16px;
      }
      .sanity-value {
        font-size: 76px;
        font-weight: 800;
        line-height: 1.5;
        color: var(--theme);
        letter-spacing: 0;
      }
      .sanity-max {
        font-size: 20px;
        color: var(--muted);
        font-weight: 600;
      }
      .sanity-state {
        margin-left: auto;
        font-size: 13px;
        letter-spacing: 2px;
        padding: 5px 14px;
        border: 1px solid var(--theme);
        border-radius: 5px;
        color: var(--theme);
      }
      .sanity-state.waiting {
        border-color: var(--line);
        color: var(--label);
      }
    </style>
  </head>
  <body>
    <div class="card {{ card_class }}">
      {% set header_title %}理智{% endset %}{% set header_meta %}{{ sanity.nickname or "未知博士" }}{% endset %}
{{ ui.card_header(header_title, header_meta) }}
      <div class="sanity-block">
        {% set sanity_unit %}/ {{ sanity.max }}{% endset %}{{ ui.metric("", sanity.current, sanity_unit, True) }}
        <span class="sanity-state {% if not sanity.full %}waiting{% endif %}">
          {% if sanity.full %}FULL{% else %}RECOVERING{% endif %}
        </span>
      </div>
      <div class="progress">
        <div class="progress-fill" style="width: {{ sanity.percent }}%"></div>
      </div>
      <div class="panel" style="margin-top: 4px">
        {% set section_title %}
          {% if sanity.full %}状态{% else %}距回满{% endif %}
        {% endset %}{{ ui.section(section_title) }}
        <div class="row">
          <span class="row-label">剩余时间</span>
          <span class="row-value accent">{{ sanity.remaining_text }}</span>
        </div>
        <div class="row">
          <span class="row-label">恢复速率</span>
          <span class="row-value">{{ sanity.recovery_minutes }} 分钟 / 点</span>
        </div>
      </div>
      <div class="card-footer">
        <span>© HYPERGRYPH · 数据时间 {{ sanity.data_time }}</span>
        <span><span class="barcode"></span><span class="serial">RI-SANITY-001</span></span>
      </div>
    </div>
  </body>
</html>
""",
    "task.html": """{% import "_macros.html" as ui %}
<!doctype html>
<html lang="zh-CN">
  <head>
    <meta charset="utf-8" />
    <style>
      {{ base_css | safe }}
      .task-grid {
        display: grid;
        grid-template-columns: 1fr 1fr;
        gap: 14px;
        margin-bottom: 6px;
      }
      .task-box {
        border: 1px solid var(--line);
        padding: 13px 15px;
      }
      .task-key {
        font-size: 12px;
        color: var(--muted);
        letter-spacing: 1.4px;
      }
      .task-val {
        display: flex;
        align-items: baseline;
        gap: 7px;
        margin: 6px 0 9px;
      }
      .task-val b {
        font-size: 27px;
        font-weight: 700;
      }
      .task-val span {
        font-size: 13px;
        color: var(--muted);
      }
      .task-box.done b {
        color: var(--accent);
      }
    </style>
  </head>
  <body>
    <div class="card {{ card_class }}">
      {% set header_title %}任务进度{% endset %}{% set header_meta %}Routine &amp; Rewards{% endset %}
{{ ui.card_header(header_title, header_meta) }}
      <div class="panel">
        {% set section_title %}日常{% endset %}{{ ui.section(section_title) }}
        <div class="task-grid">
          {% for box in [{"key": "每日任务", "node": task.daily},
                         {"key": "每周任务", "node": task.weekly}] %}
          <div class="task-box {% if box.node.percent >= 100 %}done{% endif %}">
            <div class="task-key">{{ box.key }}</div>
            <div class="task-val">
              <b>{{ box.node.current }}</b>
              <span>/ {{ box.node.total }}</span>
            </div>
            <div class="progress" style="margin: 0">
              <div class="progress-fill" style="width: {{ box.node.percent }}%"></div>
            </div>
          </div>
          {% endfor %}
        </div>
      </div>
      <div class="panel">
        {% set section_title %}周常奖励{% endset %}{{ ui.section(section_title) }}
        <div class="task-grid">
          {% for box in [{"key": "剿灭合成玉", "node": task.campaign},
                         {"key": "保全派驻 · 数据增补仪", "node": task.tower_lower}] %}
          <div class="task-box {% if box.node.percent >= 100 %}done{% endif %}">
            <div class="task-key">{{ box.key }}</div>
            <div class="task-val">
              <b>{{ box.node.current }}</b>
              <span>/ {{ box.node.total }}</span>
            </div>
            <div class="progress" style="margin: 0">
              <div class="progress-fill" style="width: {{ box.node.percent }}%"></div>
            </div>
          </div>
          {% endfor %}
        </div>
      </div>
      <div class="panel">
        {% set section_title %}保全派驻{% endset %}{{ ui.section(section_title) }}
        <div class="row">
          <span class="row-label">数据增补条</span>
          <span class="row-value">
            {{ task.tower_higher.current }} / {{ task.tower_higher.total }}
          </span>
        </div>
        <div class="progress">
          <div class="progress-fill" style="width: {{ task.tower_higher.percent }}%"></div>
        </div>
        <div class="row" style="border-bottom: none">
          <span class="row-label">结算时间</span>
          <span class="row-value">{{ task.tower_term }}</span>
        </div>
      </div>
      <div class="card-footer">
        <span>© HYPERGRYPH · 进度为上次同步快照，游戏内刷新后请重新查询</span>
        <span><span class="barcode"></span><span class="serial">RI-ROUTINE-001</span></span>
      </div>
    </div>
  </body>
</html>
""",
    "training_badges.css": """.training-badges { margin: 6px 0; font-size: 12px; line-height: 1.5; color: var(--muted); }
.skill-badges { display:flex; flex-wrap:wrap; gap:6px; justify-content:center; }
.skill-badge { display:flex; flex-direction:column; align-items:center; gap:4px; }
.skill-picture { width:25px; height:25px; position:relative; display:flex; align-items:center; justify-content:center; background:#161d2b; border:1px solid #56627d; border-radius:3px; }
.training-badges img.skill-icon { width:25px; height:25px; object-fit:contain; border:0; border-radius:2px; box-shadow:none; }
.skill-slot { position:absolute; right:-3px; bottom:-3px; background:#0e1522; color:#f4f6fb; border:1px solid #72839c; border-radius:2px; padding:0 2px; font-size:12px; line-height:18px; }
.mastery-rank { display:flex; gap:3px; height:8px; align-items:center; }
.rank-diamond { display:inline-block; width:5px; height:5px; border:1px solid #586178; transform:rotate(45deg); background:#141c2a; }
.rank-diamond.filled { background:#ffcf76; border-color:#ffe4ab; box-shadow:0 0 3px #ffc25b66; }
.module-badges { display:flex; flex-direction:column; gap:4px; margin-top:7px; }
.module-badge { display:flex; align-items:center; gap:5px; justify-content:center; }
.module-hex { flex-shrink:0; width:24px; height:25px; display:flex; align-items:center; justify-content:center; clip-path:polygon(25% 0,75% 0,100% 50%,75% 100%,25% 100%,0 50%); background:#bed7ea; color:#122031; font-size:12px; font-weight:800; }
.module-name { overflow-wrap:anywhere; font-size:12px; }
.training-empty { opacity:.75; text-align:center; display:block; }
.training-legend { font-size:12px; color:var(--muted); margin:6px 0; }
.potential-badge { display:flex; align-items:center; justify-content:center; gap:4px; margin-bottom:6px; color:#e6d3a3; font-size:12px; }
.training-badges img.potential-icon { width:20px; height:20px; object-fit:contain; border:0; box-shadow:none; }
""",
    "training_badges.html": """{% macro training(op) %}
<div class="training-badges">
  <div class="potential-badge" title="潜能 {{ op.potential_level or '未知' }}">{% if op.potential_badge_icon %}<img class="potential-icon" src="{{ op.potential_badge_icon }}" alt="" />{% endif %}<span>潜能 {{ op.potential_level if op.potential_level else '未知' }}</span></div>
  <div class="skill-badges">
  {% for skill in op.mastery_badges %}
    <div class="skill-badge" title="技能 {{ skill.slot }}：专精 {{ skill.level }}">
      <span class="skill-picture">{% if skill.icon %}<img class="skill-icon" src="{{ skill.icon }}" alt="技能 {{ skill.slot }}" />{% else %}<span>S{{ skill.slot }}</span>{% endif %}<b class="skill-slot">{{ skill.slot }}</b></span>
      <span class="mastery-rank" aria-label="专精 {{ skill.level }}">{% for n in range(1,4) %}<i class="rank-diamond{% if n <= skill.level %} filled{% endif %}"></i>{% endfor %}</span>
    </div>
  {% else %}<span class="training-empty">暂无技能数据</span>{% endfor %}
  </div>
  <div class="module-badges">
  {% for module in op.unlocked_modules %}
    <span class="module-badge" title="{{ module.name }}：模组等级 {{ module.level }}"><span class="module-hex">{{ ['','I','II','III'][module.level] if module.level >= 0 and module.level <= 3 else module.level }}</span><span class="module-name">{{ module.name }}</span></span>
  {% else %}<span class="training-empty">无已开启模组</span>{% endfor %}
  </div>
</div>
{% endmacro %}
""",
}


def get(name: str) -> str:
    """Return an embedded template.

    Args:
        name: Template name, including its extension.

    Returns:
        The original template content.

    Raises:
        KeyError: If the template name is unknown.
    """
    return TEMPLATES[name]


def names() -> tuple[str, ...]:
    """Return the available embedded template names.

    Returns:
        Template names in their stored order.
    """
    return tuple(TEMPLATES)
