"""Render the GitHub profile README and its banner from saahil.co.uk/status.json.

    python scripts/render_readme.py                       # fetch the live JSON
    python scripts/render_readme.py --source status.json  # or a local file

Writes README.md, assets/banner-{light,dark}.svg and assets/platform-{light,dark}.svg. The banner carries the statement in
Mona Sans with the vermilion underline drawn once, the role line, and the featured systems'
stills embedded as data URIs, so it renders the same wherever GitHub proxies it. The README
below it is plain Markdown in the site's voice. Needs Pillow for the still thumbnails.
"""
from __future__ import annotations

import argparse
import base64
import io
import json
import urllib.request
from datetime import datetime, timezone
from pathlib import Path
from xml.sax.saxutils import escape

from fontTools.ttLib import TTFont
from fontTools.varLib.instancer import instantiateVariableFont
from PIL import Image

ROOT = Path(__file__).resolve().parent.parent
ASSETS = ROOT / "assets"
FONT = ASSETS / "fonts" / "mona-sans.woff2"
README = ROOT / "README.md"
UA = "smehta/profile-readme-render"
WIDTH = 1200
MEASURE = None  # set in main once the font is known to exist

THEMES = {
    "dark": {"field": "#0c0c0e", "ink": "#f2efe9", "ink2": "#b3aea5", "ink3": "#8a857d", "accent": "#ff4a1c", "still": "still"},
    "light": {"field": "#f3f1ec", "ink": "#15140f", "ink2": "#5b5852", "ink3": "#6d6962", "accent": "#c8350d", "still": "still_light"},
}
MONTHS = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
STATE = {"live": "In production", "in_progress": "In build", "paused": "Paused", "archived": "Retired"}


def fetch(url: str) -> bytes:
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    with urllib.request.urlopen(req, timeout=60) as res:
        return res.read()


def month_label(ym: str | None) -> str:
    if not ym or ym == "present":
        return "present"
    y, m = ym.split("-")
    return f"{MONTHS[int(m) - 1]} {y}"


def thumb(url: str, size: int = 400) -> str:
    """A still, downscaled and re-encoded as a WebP data URI."""
    im = Image.open(io.BytesIO(fetch(url))).convert("RGBA").resize((size, size), Image.LANCZOS)
    buf = io.BytesIO()
    im.save(buf, "WEBP", quality=80, method=6)
    return "data:image/webp;base64," + base64.b64encode(buf.getvalue()).decode()


class Measure:
    """Exact advances for Mona Sans at the banner's weight and width, so the underline sits
    under the letters it belongs to and lines wrap on real widths."""

    def __init__(self, path: Path, wght: float = 560, wdth: float = 98, tracking_em: float = -0.03):
        font = instantiateVariableFont(TTFont(str(path)), {"wght": wght, "wdth": wdth})
        self.cmap = font.getBestCmap()
        self.hmtx = font["hmtx"]
        self.upm = font["head"].unitsPerEm
        self.tracking = tracking_em

    def width(self, text: str, size: float) -> float:
        units = sum(self.hmtx[self.cmap.get(ord(ch), self.cmap.get(32))][0] for ch in text)
        return units / self.upm * size + len(text) * self.tracking * size

    def wrap(self, text: str, size: float, max_px: float) -> list[str]:
        words, lines, cur = text.split(), [], ""
        for w in words:
            cand = f"{cur} {w}".strip()
            if self.width(cand, size) <= max_px:
                cur = cand
            else:
                lines.append(cur)
                cur = w
        if cur:
            lines.append(cur)
        return lines


def banner(data: dict, theme: str, thumbs: dict[str, str]) -> str:
    c = THEMES[theme]
    n = data["narrative"]
    font = base64.b64encode(FONT.read_bytes()).decode()
    statement, key = n["statement"], n["statement_key"]
    m = MEASURE
    # Two bands: the statement and role line across the top, the featured stills in a row
    # beneath, each with its name. The statement wraps on measured widths in a 1040px column.
    size, lh, x0, y0 = 60, 66, 56, 100
    lines = m.wrap(statement, size, WIDTH - 2 * x0 - 48)
    text_rows = [f'<text x="{x0}" y="{y0 + i * lh}" class="t" font-size="{size}" fill="{c["ink"]}">{escape(line)}</text>' for i, line in enumerate(lines)]
    # The key phrase takes the drawn underline; it may span a line break, so each line's
    # overlap with the phrase is underlined on its own, at measured positions.
    pos = statement.find(key)
    rules, cursor, delay = [], 0, 0.9
    for i, line in enumerate(lines):
        start, end = cursor, cursor + len(line)
        a, b = max(start, pos), min(end, pos + len(key))
        if a < b:
            x1 = x0 + m.width(line[: a - start], size)
            w = m.width(line[a - start : b - start], size)
            rules.append(f'<rect class="u" x="{x1:.1f}" y="{y0 + i * lh + 10}" width="{w:.1f}" height="4" fill="{c["accent"]}" style="animation-delay:{delay:.2f}s"/>')
            delay += 0.35
        cursor = end + 1
    role_y = y0 + len(lines) * lh + 16
    updated = datetime.fromisoformat(data["generated_at"].replace("Z", "+00:00")).astimezone(timezone.utc)
    featured = [p for p in data["components"] if p["name"] in data["featured"]]
    tile = 150
    sy = role_y + 56
    h = sy + tile + 34 + 58
    cols = max(len(featured), 1)
    span = (WIDTH - 2 * x0) / cols
    stills = []
    for i, p in enumerate(featured):
        cx = x0 + span * i + span / 2
        x = cx - tile / 2
        stills.append(f'<image class="s" href="{thumbs[p[c["still"]]]}" x="{x:.0f}" y="{sy}" width="{tile}" height="{tile}" style="animation-delay:{0.3 + i * 0.12:.2f}s"/>')
        stills.append(f'<text class="t" x="{cx:.0f}" y="{sy + tile + 26}" font-size="14" text-anchor="middle" fill="{c["ink3"]}">{escape(p["name"])}</text>')
    label = f"{escape(statement)} {escape(n['role_line'])}"
    return f"""<svg xmlns="http://www.w3.org/2000/svg" width="{WIDTH}" height="{h}" viewBox="0 0 {WIDTH} {h}" role="img" aria-label="{label}">
<defs><style>
@font-face{{font-family:"Mona Sans";font-weight:200 900;font-stretch:75% 125%;src:url(data:font/woff2;base64,{font}) format("woff2")}}
.t{{font-family:"Mona Sans",Helvetica,Arial,sans-serif;font-weight:560;font-stretch:98%;letter-spacing:-0.03em}}
.r{{font-family:"Mona Sans",Helvetica,Arial,sans-serif;font-weight:400;letter-spacing:0}}
.c{{font-family:"Mona Sans",Helvetica,Arial,sans-serif;font-weight:540;letter-spacing:0.08em;text-transform:uppercase}}
.u{{transform-origin:left center;transform:scaleX(0);animation:draw 900ms cubic-bezier(0.16,1,0.3,1) forwards}}
.s{{opacity:0;animation:rise 700ms cubic-bezier(0.16,1,0.3,1) forwards}}
@keyframes draw{{to{{transform:scaleX(1)}}}}
@keyframes rise{{from{{opacity:0;transform:translateY(10px)}}to{{opacity:1;transform:none}}}}
@media (prefers-reduced-motion: reduce){{.u{{transform:none;animation:none}}.s{{opacity:1;animation:none}}}}
</style></defs>
<rect width="{WIDTH}" height="{h}" fill="{c["field"]}"/>
{"".join(rules)}
{"".join(text_rows)}
<text x="{x0}" y="{role_y}" class="r" font-size="20" fill="{c["ink2"]}">{escape(n["role_line"])}</text>
{"".join(stills)}
<text x="{x0}" y="{h - 28}" class="c" font-size="11" fill="{c["ink3"]}">Updated {updated.strftime('%-d %b %Y')} · saahil.co.uk</text>
</svg>
"""


def diagram_section(data: dict) -> str:
    """The platform diagram the site renders, embedded in both schemes from the files
    status.json links; nothing is drawn here. Absent from an older status.json, the section is left out."""
    d = (data.get("diagrams") or {}).get("platform")
    if not d:
        return ""
    for theme in ("dark", "light"):
        (ASSETS / f"platform-{theme}.svg").write_bytes(fetch(d[theme]))
    note = (data.get("ecosystem") or {}).get("note") or ""
    return f"""## {d["title"]}

{d["lede"]}

<picture>
  <source media="(prefers-color-scheme: dark)" srcset="assets/platform-dark.svg">
  <img alt="{escape(d["title"])}. {escape(d["lede"])}" src="assets/platform-light.svg" width="100%">
</picture>

{note}
"""


def readme(data: dict) -> str:
    n, o, f = data["narrative"], data["operator"], data["files"]
    featured = [p for p in data["components"] if p["name"] in data["featured"]]
    others = [p for p in data["components"] if p["name"] not in data["featured"] and p["status"] in ("live", "in_progress")]
    roles = data["releases"]
    host = o["url"].replace("https://", "")
    out = [f'''<a href="{o["url"]}">
  <picture>
    <source media="(prefers-color-scheme: dark)" srcset="assets/banner-dark.svg">
    <img alt="{escape(n["statement"])} {escape(n["role_line"])}" src="assets/banner-light.svg" width="100%">
  </picture>
</a>
''', "## Now\n"]
    out.extend(f"{line}\n" for line in n["now"])
    out.append(f"\n## Work\n\n{n['ledes']['work']}\n")
    for p in featured + others:
        since = f"since {month_label(p['since'])}" if not p["until"] else f"{month_label(p['since'])} to {month_label(p['until'])}"
        name = f"[{p['name']}]({p['link']})" if p.get("link") else p["name"]
        out.append(f"- **{name}** · {p['category']}, {STATE[p['status']].lower()} {since}. {p['opening']}")
    out.append(f"\nAll systems, with how each is built: [{host}/projects]({o['url']}/projects).\n")
    out.append(f"## Still shipping\n\n{n['ledes']['shipping'].replace('live from GitHub', 'drawn by GitHub beneath this page')}\n")
    section = diagram_section(data)
    if section:
        out.append(section)
    out.append(f"## Experience\n\n{n['ledes']['experience']}\n")
    for r in roles[:3]:
        where = f"{r['org']}{', ' + r['unit'] if r.get('unit') else ''}"
        out.append(f"- **{r['title']}**, {where}, {month_label(r['start'])} to {month_label(r['end'])}. {r['line']}")
    out.append(f"\nFull history: [{host}/experience]({o['url']}/experience).\n")
    out.append(f"## Beyond work\n\n{n['ledes']['beyond']}\n")
    for v in data["community"]:
        name = f"[{v['name']}]({v['link']})" if v.get("link") else v["name"]
        out.append(f"- **{name}**, {v['venue']}, {v['year']}.")
    for e in data["education"][:1]:
        out.append(f"- **{e['degree']}**, {e['org']}, {e['years']}. {e['grade']}.")
    out.append(f"\n## {n['end_card']}\n\n{n['ledes']['contact']}\n")
    out.append(f"[{o['email']}](mailto:{o['email']}) · [LinkedIn]({o['linkedin']}) · [Book a call]({o['book_a_call']})\n")
    out.append(f"<sub>Also available as [resume.pdf]({f['resume_pdf']}) · [resume.json]({f['resume_json']}) · [cv.md]({f['cv_md']}) · [llms.txt]({f['llms_txt']}) · [status.json]({f['status_json']}). This page re-renders every morning from status.json, the same source the site builds from.</sub>\n")
    return "\n".join(out)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source", default="https://saahil.co.uk/status.json")
    args = parser.parse_args()
    raw = Path(args.source).read_bytes() if Path(args.source).exists() else fetch(args.source)
    data = json.loads(raw)
    global MEASURE
    MEASURE = Measure(FONT)
    featured = [p for p in data["components"] if p["name"] in data["featured"]]
    thumbs = {p[key]: thumb(p[key]) for p in featured for key in ("still", "still_light")}
    ASSETS.mkdir(exist_ok=True)
    for theme in THEMES:
        path = ASSETS / f"banner-{theme}.svg"
        path.write_text(banner(data, theme, thumbs), encoding="utf-8")
        print(f"wrote {path.relative_to(ROOT)} ({path.stat().st_size // 1024} KB)")
    README.write_text(readme(data), encoding="utf-8")
    print(f"wrote README.md ({len(README.read_text().splitlines())} lines)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
