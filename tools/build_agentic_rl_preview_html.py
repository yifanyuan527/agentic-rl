#!/usr/bin/env python3
"""Build a browser-viewable HTML preview for the Agentic RL slide deck."""
from __future__ import annotations

import html
from pathlib import Path

from build_agentic_rl_pptx import SRC, parse_slides

ROOT = Path(__file__).resolve().parents[1]
HTML_OUT = ROOT / "reports" / "agentic_rl_survey_cn_preview.html"
SVG_OUT = ROOT / "reports" / "agentic_rl_survey_cn_preview.svg"
FIRST6_SVG_OUT = ROOT / "reports" / "agentic_rl_survey_cn_preview_first6.svg"

CSS = """
:root {
  color-scheme: light;
  --bg: #eef2f7;
  --slide-bg: #f8fafc;
  --card: #ffffff;
  --text: #0f172a;
  --muted: #64748b;
  --border: #e2e8f0;
  --accent: #2563eb;
}
* { box-sizing: border-box; }
body {
  margin: 0;
  background: var(--bg);
  color: var(--text);
  font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", "Microsoft YaHei", "PingFang SC", Arial, sans-serif;
}
.header {
  position: sticky;
  top: 0;
  z-index: 10;
  padding: 18px 28px;
  background: rgba(255,255,255,0.92);
  border-bottom: 1px solid var(--border);
  backdrop-filter: blur(10px);
}
.header h1 { margin: 0 0 6px; font-size: 24px; }
.header p { margin: 0; color: var(--muted); font-size: 14px; }
.deck {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(520px, 1fr));
  gap: 28px;
  padding: 28px;
}
.slide {
  aspect-ratio: 16 / 9;
  background: var(--slide-bg);
  border: 1px solid #cbd5e1;
  border-radius: 16px;
  box-shadow: 0 18px 48px rgba(15, 23, 42, 0.14);
  padding: 30px 34px;
  display: flex;
  flex-direction: column;
  position: relative;
  overflow: hidden;
}
.slide::before {
  content: "";
  position: absolute;
  top: 0;
  left: 0;
  width: 8px;
  height: 100%;
  background: linear-gradient(180deg, #2563eb, #7c3aed, #059669);
}
.title {
  margin: 0 0 18px 6px;
  font-size: 28px;
  line-height: 1.2;
  letter-spacing: -0.02em;
}
.body {
  margin-left: 22px;
  padding: 22px 26px;
  background: var(--card);
  border: 1px solid var(--border);
  border-radius: 18px;
  flex: 1;
}
ul { margin: 0; padding-left: 22px; }
li {
  margin: 0 0 12px;
  font-size: 17px;
  line-height: 1.45;
}
.footer {
  margin: 15px 0 0 6px;
  color: var(--muted);
  font-size: 13px;
  display: flex;
  justify-content: space-between;
}
@media (max-width: 640px) {
  .deck { grid-template-columns: 1fr; padding: 14px; gap: 18px; }
  .slide { padding: 22px; border-radius: 12px; }
  .title { font-size: 20px; }
  .body { margin-left: 10px; padding: 16px; }
  li { font-size: 13px; margin-bottom: 8px; }
}
"""


def render_slide(num: int, title: str, bullets: list[str], total: int) -> str:
    bullet_html = "\n".join(f"<li>{html.escape(b)}</li>" for b in bullets[:6])
    return f"""
<section class="slide" id="slide-{num}">
  <h2 class="title">{html.escape(title)}</h2>
  <div class="body"><ul>{bullet_html}</ul></div>
  <div class="footer"><span>Agentic RL 中文调研报告</span><span>{num:02d} / {total:02d}</span></div>
</section>
"""


def wrap_text(text: str, limit: int = 31) -> list[str]:
    lines: list[str] = []
    current = ""
    for part in text.split():
        candidate = part if not current else current + " " + part
        if len(candidate) <= limit:
            current = candidate
        else:
            if current:
                lines.append(current)
            while len(part) > limit:
                lines.append(part[:limit])
                part = part[limit:]
            current = part
    if current:
        lines.append(current)
    return lines or [""]


def render_svg(slides: list[tuple[str, list[str]]]) -> str:
    slide_w, slide_h, gap, margin = 960, 540, 36, 40
    cols = 2
    rows = (len(slides) + cols - 1) // cols
    width = margin * 2 + cols * slide_w + (cols - 1) * gap
    height = margin * 2 + rows * slide_h + (rows - 1) * gap
    parts = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}">', '<rect width="100%" height="100%" fill="#eef2f7"/>']
    for idx, (title, bullets) in enumerate(slides, 1):
        col, row = (idx - 1) % cols, (idx - 1) // cols
        x, y = margin + col * (slide_w + gap), margin + row * (slide_h + gap)
        parts.extend([
            f'<g transform="translate({x},{y})">',
            '<rect width="960" height="540" rx="18" fill="#f8fafc" stroke="#cbd5e1"/>',
            '<rect width="8" height="540" rx="4" fill="#2563eb"/>',
            f'<text x="34" y="58" font-family="Microsoft YaHei, PingFang SC, Arial, sans-serif" font-size="28" font-weight="700" fill="#0f172a">{html.escape(title)}</text>',
            '<rect x="58" y="105" width="842" height="355" rx="18" fill="#ffffff" stroke="#e2e8f0"/>',
        ])
        ty = 145
        for bullet in bullets[:6]:
            lines = wrap_text(bullet, 36)[:2]
            parts.append(f'<text x="86" y="{ty}" font-family="Microsoft YaHei, PingFang SC, Arial, sans-serif" font-size="18" fill="#0f172a">• {html.escape(lines[0])}</text>')
            ty += 25
            for line in lines[1:]:
                parts.append(f'<text x="106" y="{ty}" font-family="Microsoft YaHei, PingFang SC, Arial, sans-serif" font-size="18" fill="#0f172a">{html.escape(line)}</text>')
                ty += 25
            ty += 10
        parts.append(f'<text x="34" y="506" font-family="Microsoft YaHei, PingFang SC, Arial, sans-serif" font-size="14" fill="#64748b">Agentic RL 中文调研报告 · {idx:02d}</text>')
        parts.append('</g>')
    parts.append('</svg>')
    return "\n".join(parts)


def main() -> None:
    slides = parse_slides(SRC.read_text(encoding="utf-8"))
    total = len(slides)
    body = "\n".join(render_slide(i, title, bullets, total) for i, (title, bullets) in enumerate(slides, 1))
    HTML_OUT.write_text(
        f"""<!doctype html>
<html lang="zh-CN">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>Agentic RL 中文调研报告 PPT 预览</title>
  <style>{CSS}</style>
</head>
<body>
  <header class="header">
    <h1>Agentic RL 中文调研报告 PPT 预览</h1>
    <p>这是 PPTX 的浏览器预览版：16:9 卡片、标题、正文卡片和页脚布局与生成的 PPTX 保持一致。</p>
  </header>
  <main class="deck">{body}</main>
</body>
</html>
""",
        encoding="utf-8",
    )
    SVG_OUT.write_text(render_svg(slides), encoding="utf-8")
    FIRST6_SVG_OUT.write_text(render_svg(slides[:6]), encoding="utf-8")
    print(f"Wrote {HTML_OUT}, {SVG_OUT}, and {FIRST6_SVG_OUT} ({total} slides)")


if __name__ == "__main__":
    main()
