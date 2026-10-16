"""Render the profile README's status graphics from saahil.co.uk/status.json.

    python scripts/render_status.py                       # fetch the live JSON
    python scripts/render_status.py --source status.json  # or a local file

Writes assets/banner-{light,dark}.svg and assets/components-{light,dark}.svg. Fonts are
embedded as data URIs so the SVGs render identically wherever GitHub proxies them. No
dependencies beyond the standard library.
"""
from __future__ import annotations

import argparse
import base64
import json
import urllib.request
from datetime import datetime, timezone
from pathlib import Path
from xml.sax.saxutils import escape

ROOT = Path(__file__).resolve().parent.parent
ASSETS = ROOT / "assets"
FONTS = ASSETS / "fonts"
WIDTH = 1200

THEMES = {
    "light": {
        "ground": "#ffffff", "ground2": "#f4f6f8", "ink": "#0f1419", "ink2": "#4b5563", "ink3": "#6b7280",
        "rule": "#e3e7eb", "field": "#0b6b40", "field2": "#0f7f4c", "on_field": "#ffffff",
        "cell_off": "#e9ecef", "green_cell": "#1f9d5f", "amber_cell": "#e3a63b", "grey_cell": "#c2c8cf",
        "green_soft": "#d8f1e3", "green_ink": "#0a6b3e", "amber_soft": "#fbefd6", "amber_ink": "#7a4d0b",
        "grey_soft": "#eef0f3", "grey_ink": "#4b5563", "dot": "#7ff0b2",
    },
    "dark": {
        "ground": "#0b0d10", "ground2": "#121519", "ink": "#e8eaed", "ink2": "#b4bac2", "ink3": "#8b929b",
        "rule": "#1f242a", "field": "#0c5a37", "field2": "#0f6b41", "on_field": "#eafff3",
        "cell_off": "#1a1f25", "green_cell": "#2bbf6f", "amber_cell": "#d99a2b", "grey_cell": "#3a4148",
        "green_soft": "#0f2d1e", "green_ink": "#4ade80", "amber_soft": "#2d2410", "amber_ink": "#f0b454",
        "grey_soft": "#1a1f25", "grey_ink": "#b4bac2", "dot": "#7ff0b2",
    },
}
STATUS_LABEL = {"live": "Operational", "in_progress": "In build", "paused": "Paused", "archived": "Retired"}
MONTHS = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
CHECK_PATH = "M12 22a10 10 0 1 0 0-20 10 10 0 0 0 0 20Zm-3.5-10 2.5 2.5 5-5"


def font_face(family: str, file: str, weight: int) -> str:
    data = base64.b64encode((FONTS / file).read_bytes()).decode()
    return (f'@font-face{{font-family:"{family}";font-weight:{weight};'
            f'src:url(data:font/woff2;base64,{data}) format("woff2")}}')


def styles() -> str:
    return (
        "<style>"
        + font_face("Bricolage", "bricolage-600.woff2", 600)
        + font_face("Mono", "jetbrains-mono-500.woff2", 500)
        + '.d{font-family:"Bricolage",Helvetica,Arial,sans-serif;font-weight:600;letter-spacing:-0.01em}'
        + '.s{font-family:-apple-system,BlinkMacSystemFont,"Segoe UI",Helvetica,Arial,sans-serif}'
        + '.m{font-family:"Mono",ui-monospace,Menlo,monospace;font-weight:500}'
        + "</style>"
    )


def month_label(ym: str) -> str:
    y, m = ym.split("-")
    return f"{MONTHS[int(m) - 1]} {y}"


def month_index(ym: str) -> int:
    y, m = ym.split("-")
    return int(y) * 12 + int(m) - 1


def wrap(text: str, max_px: float, size: float, max_lines: int = 2) -> list[str]:
    """Greedy word wrap on an average glyph width; good enough for a two-line summary."""
    per_char = size * 0.5
    words, lines, current = text.split(), [], ""
    for w in words:
        candidate = f"{current} {w}".strip()
        if len(candidate) * per_char <= max_px:
            current = candidate
        else:
            lines.append(current)
            current = w
            if len(lines) == max_lines:
                break
    if len(lines) < max_lines and current:
        lines.append(current)
    if len(lines) == max_lines and len(" ".join(lines)) < len(text):
        lines[-1] = lines[-1].rstrip(".,;") + "…"
    return lines[:max_lines]


def banner(data: dict, theme: str) -> str:
    c = THEMES[theme]
    b = data["banner"]
    checked = datetime.fromisoformat(data["generated_at"].replace("Z", "+00:00")).astimezone(timezone.utc)
    sub = f"{b['operational']} operational · {b['in_build']} in build · {b['people_served']:,} people served · one operator"
    h = 150
    return f"""<svg xmlns="http://www.w3.org/2000/svg" width="{WIDTH}" height="{h}" viewBox="0 0 {WIDTH} {h}" role="img" aria-label="{escape(b['heading'])}. {escape(sub)}">
<defs>{styles()}<linearGradient id="g" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="{c['field2']}"/><stop offset="1" stop-color="{c['field']}"/></linearGradient></defs>
<rect width="{WIDTH}" height="{h}" rx="14" fill="url(#g)"/>
<g transform="translate(48 55) scale(1.75)" fill="none" stroke="{c['dot']}" stroke-width="1.75" stroke-linecap="round" stroke-linejoin="round"><path d="{CHECK_PATH}"/></g>
<text x="108" y="72" class="d" font-size="42" fill="{c['on_field']}">{escape(b['heading'])}</text>
<text x="108" y="104" class="s" font-size="19" fill="{c['on_field']}" fill-opacity="0.82">{escape(sub)}</text>
<text x="{WIDTH - 48}" y="62" class="m" font-size="13" text-anchor="end" fill="{c['on_field']}" fill-opacity="0.78">Last checked</text>
<text x="{WIDTH - 48}" y="84" class="m" font-size="14" text-anchor="end" fill="{c['on_field']}">{checked.strftime('%Y-%m-%d %H:%M UTC')}</text>
<text x="{WIDTH - 48}" y="116" class="m" font-size="13" text-anchor="end" fill="{c['on_field']}" fill-opacity="0.78">saahil.co.uk</text>
</svg>
"""


def components(data: dict, theme: str) -> str:
    c = THEMES[theme]
    rows = [p for p in data["components"] if p["status"] in ("live", "in_progress")]
    now = month_index(data["month"])
    row_h, head_h, pad = 112, 44, 48
    h = head_h + row_h * len(rows) + 24
    out = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{WIDTH}" height="{h}" viewBox="0 0 {WIDTH} {h}" role="img" aria-label="Components in production">',
           f"<defs>{styles()}</defs>", f'<rect width="{WIDTH}" height="{h}" rx="14" fill="{c["ground"]}"/>']
    # header row
    x_strip, strip_w, x_fig, x_pill = 500, 260, 1010, 1046
    out.append(f'<text x="{pad}" y="28" class="m" font-size="12" fill="{c["ink3"]}">Component</text>')
    out.append(f'<text x="{x_strip}" y="28" class="m" font-size="12" fill="{c["ink3"]}">Time in production, last 36 months</text>')
    out.append(f'<text x="{x_fig}" y="28" class="m" font-size="12" text-anchor="end" fill="{c["ink3"]}">Headline figure</text>')
    out.append(f'<text x="{x_pill}" y="28" class="m" font-size="12" fill="{c["ink3"]}">Status</text>')
    out.append(f'<line x1="{pad}" x2="{WIDTH - pad}" y1="{head_h}" y2="{head_h}" stroke="{c["rule"]}"/>')
    for i, p in enumerate(rows):
        y = head_h + i * row_h
        cy = y + row_h / 2
        # name, venue, summary
        out.append(f'<text x="{pad}" y="{y + 36}" class="d" font-size="20" fill="{c["ink"]}">{escape(p["name"])}</text>')
        name_w = len(p["name"]) * 20 * 0.56 + 10
        venue_w = len(p["venue"]) * 13 * 0.52
        # The venue sits beside the name while both fit in the column; otherwise it drops below.
        if name_w + venue_w <= 420:
            out.append(f'<text x="{pad + name_w}" y="{y + 36}" class="s" font-size="13" fill="{c["ink3"]}">{escape(p["venue"])}</text>')
            summary_y = y + 60
        else:
            out.append(f'<text x="{pad}" y="{y + 54}" class="s" font-size="13" fill="{c["ink3"]}">{escape(p["venue"])}</text>')
            summary_y = y + 76
        first = p["summary"].split(". ")[0].rstrip(".") + "."
        max_lines = 2 if summary_y == y + 60 else 1
        for j, line in enumerate(wrap(first, 400, 14.5, max_lines)):
            out.append(f'<text x="{pad}" y="{summary_y + j * 20}" class="s" font-size="14.5" fill="{c["ink2"]}">{escape(line)}</text>')
        # strip
        start, stop = month_index(p["since"]), month_index(p["until"]) if p["until"] else now
        cell_w = (strip_w - 35 * 2) / 36
        fill_on = {"live": c["green_cell"], "in_progress": c["amber_cell"]}.get(p["status"], c["grey_cell"])
        for k in range(36):
            m = now - 35 + k
            on = start <= m <= stop
            out.append(f'<rect x="{x_strip + k * (cell_w + 2):.2f}" y="{cy - 14}" width="{cell_w:.2f}" height="20" rx="2" fill="{fill_on if on else c["cell_off"]}"/>')
        span = f"{month_label(p['since'])} to {'now' if not p['until'] else month_label(p['until'])}"
        out.append(f'<text x="{x_strip}" y="{cy + 24}" class="m" font-size="11" fill="{c["ink3"]}">{escape(span)}</text>')
        out.append(f'<text x="{x_strip + strip_w}" y="{cy + 24}" class="m" font-size="11" text-anchor="end" fill="{c["ink3"]}">{escape(p["duration"])}</text>')
        # figure
        out.append(f'<text x="{x_fig}" y="{cy - 2}" class="d" font-size="22" text-anchor="end" fill="{c["ink"]}">{escape(p["metric"]["value"])}</text>')
        out.append(f'<text x="{x_fig}" y="{cy + 18}" class="s" font-size="12" text-anchor="end" fill="{c["ink3"]}">{escape(p["metric"]["label"])}</text>')
        # pill
        label = STATUS_LABEL[p["status"]]
        soft, ink = {"live": (c["green_soft"], c["green_ink"]), "in_progress": (c["amber_soft"], c["amber_ink"])}.get(p["status"], (c["grey_soft"], c["grey_ink"]))
        pill_w = len(label) * 13 * 0.55 + 34
        out.append(f'<rect x="{x_pill}" y="{cy - 14}" width="{pill_w:.0f}" height="28" rx="14" fill="{soft}"/>')
        out.append(f'<circle cx="{x_pill + 14}" cy="{cy}" r="4" fill="{ink}"/>')
        out.append(f'<text x="{x_pill + 24}" y="{cy + 4.5}" class="s" font-size="13" font-weight="500" fill="{ink}">{label}</text>')
        out.append(f'<line x1="{pad}" x2="{WIDTH - pad}" y1="{y + row_h}" y2="{y + row_h}" stroke="{c["rule"]}"/>')
    out.append("</svg>\n")
    return "\n".join(out)


def load(source: str) -> dict:
    if source.startswith("http"):
        req = urllib.request.Request(source, headers={"User-Agent": "smehta/profile-status-render"})
        with urllib.request.urlopen(req, timeout=30) as r:
            return json.load(r)
    return json.loads(Path(source).read_text(encoding="utf-8"))


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--source", default="https://saahil.co.uk/status.json")
    args = ap.parse_args()
    data = load(args.source)
    ASSETS.mkdir(exist_ok=True)
    for theme in THEMES:
        (ASSETS / f"banner-{theme}.svg").write_text(banner(data, theme), encoding="utf-8")
        (ASSETS / f"components-{theme}.svg").write_text(components(data, theme), encoding="utf-8")
    print(f"rendered 4 svgs from {args.source} ({data['month']})")


if __name__ == "__main__":
    main()
