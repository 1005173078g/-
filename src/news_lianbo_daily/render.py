from __future__ import annotations

from html import escape
from pathlib import Path

from .models import Brief, Mainline


COLORS = ["green", "blue", "orange", "purple", "cyan", "rose"]


def render_html(brief: Brief) -> str:
    cards = "\n".join(_render_card(index, item) for index, item in enumerate(brief.mainlines, start=1))
    order = " > ".join(escape(item) for item in brief.observation_order)
    tracking = "".join(f"<li>{escape(item)}</li>" for item in brief.tracking_points)
    signals = "、".join(escape(item) for item in brief.marginal_signals)
    return f"""<!doctype html>
<html lang="zh-CN">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>{escape(brief.title)}</title>
  <style>
    body {{ margin: 0; background: #fff8ef; color: #242424; font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", "Microsoft YaHei", sans-serif; }}
    .page {{ max-width: 920px; margin: 0 auto; padding: 18px 14px 28px; }}
    .hero {{ background: #ffe1d2; border-radius: 18px; padding: 22px 18px; margin-bottom: 18px; }}
    h1 {{ margin: 0 0 8px; font-size: 30px; line-height: 1.2; }}
    .sub {{ color: #c65d3e; font-weight: 700; }}
    .formula, .summary {{ background: #fff; border: 1px solid #eadfcf; border-radius: 14px; padding: 16px; margin: 14px 0; }}
    .formula strong {{ color: #2f7eb9; font-size: 20px; }}
    .grid {{ display: grid; grid-template-columns: repeat(2, minmax(0, 1fr)); gap: 14px; }}
    .card {{ background: #fff; border: 1px solid #eadfcf; border-radius: 14px; padding: 16px; min-height: 210px; }}
    .card h2 {{ font-size: 19px; margin: 0 0 14px; padding: 9px 12px; border-radius: 12px; }}
    .green h2 {{ background: #e7f4e7; }} .blue h2 {{ background: #e8f0fb; }} .orange h2 {{ background: #ffeadb; }}
    .purple h2 {{ background: #efe9ff; }} .cyan h2 {{ background: #e4f5f3; }} .rose h2 {{ background: #ffe8ed; }}
    .label {{ color: #d05d3d; font-weight: 800; }}
    .row {{ margin: 11px 0; line-height: 1.65; color: #555; }}
    .watch {{ border-top: 1px solid #e8ddce; padding-top: 12px; color: #222; font-weight: 800; }}
    .order {{ color: #d05d3d; font-weight: 800; }}
    .footer {{ color: #8a8178; font-size: 13px; margin-top: 18px; line-height: 1.7; }}
    a {{ color: #2f7eb9; word-break: break-all; }}
    @media (max-width: 720px) {{ .grid {{ grid-template-columns: 1fr; }} h1 {{ font-size: 25px; }} }}
  </style>
</head>
<body>
  <main class="page">
    <section class="hero">
      <h1>{escape(brief.title)}</h1>
      <div class="sub">精选观察版｜新闻信号 → 产业逻辑 → 观察</div>
      <p>{escape(brief.opening)}</p>
    </section>
    <section class="formula">
      <strong>筛选公式</strong>
      <p>政策催化 → 产业逻辑 → 核心板块 → 观察标的</p>
    </section>
    <section class="grid">
      {cards}
    </section>
    <section class="summary">
      <h2>观察顺序</h2>
      <p class="order">{order}</p>
      <h2>跟踪要点</h2>
      <ul>{tracking}</ul>
      <h2>边际信号</h2>
      <p>{signals}</p>
    </section>
    <section class="footer">
      <p>央视官方来源：<a href="{escape(brief.source_url)}">{escape(brief.source_url)}</a></p>
      <p>{escape(brief.disclaimer)}</p>
    </section>
  </main>
</body>
</html>
"""


def _render_card(index: int, mainline: Mainline) -> str:
    color = COLORS[(index - 1) % len(COLORS)]
    watch = "、".join(escape(item) for item in mainline.watch)
    return f"""<article class="card {color}">
  <h2>{index} {escape(mainline.name)}｜{escape(mainline.tag)}</h2>
  <p class="row"><span class="label">消息面：</span>{escape(mainline.news)}</p>
  <p class="row"><span class="label">逻辑：</span>{escape(mainline.logic)}</p>
  <p class="watch"><span class="label">观察：</span>{watch}</p>
</article>"""


def write_html(brief: Brief, daily_dir: str | Path) -> Path:
    path = brief.to_page_path(daily_dir)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(render_html(brief), encoding="utf-8")
    return path
