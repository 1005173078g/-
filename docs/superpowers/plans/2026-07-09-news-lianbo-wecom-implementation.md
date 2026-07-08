# 《新闻联播》企业微信日报自动化 Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 搭建一套每天 21:30 自动生成《新闻联播》产业观察 HTML、发布到 GitHub Pages、并发送企业微信群链接的轻量项目。

**Architecture:** 项目用 Python 标准库实现本地可测试的渲染、校验、企业微信发送和 GitHub Pages 文件生成。每日“读取央视官方内容并提炼主线”的工作由 Codex 定时任务完成，定时任务把结构化 JSON 写入仓库，再调用项目脚本生成 HTML、提交推送、发送企业微信消息。

**Tech Stack:** Python 3 标准库、`unittest`、GitHub Pages 静态页面、企业微信群机器人 Webhook、Codex cron 自动化。

## 全局约束

- 所有文档、页面、脚本注释、企业微信消息均使用中文。
- 新闻来源使用央视网/CCTV 官方《新闻联播》文字稿或视频页面。
- 主线数量按当天内容动态生成，不固定为 6 条。
- 每条主线包含 `消息面`、`逻辑`、`观察`。
- 投资表达使用 `观察`，不使用 `推荐`、`买入`、`确定性机会`。
- 页面加入免责声明：内容仅为信息整理和学习观察，不构成投资建议。
- 企业微信 Webhook 不提交到公开仓库，只从环境变量或本地配置读取。
- 每天北京时间 21:30 运行。

---

## 文件结构

- 创建：`.gitignore`
  - 忽略本地密钥、运行缓存、Python 缓存。
- 创建：`.nojekyll`
  - 让 GitHub Pages 直接按静态文件服务仓库内容。
- 创建：`config.example.json`
  - 提供非敏感配置示例。
- 创建：`data/.gitkeep`
  - 保存每日结构化 JSON 的目录。
- 创建：`daily/.gitkeep`
  - 保存每日 HTML 页面，最终链接形如 `https://1005173078g.github.io/-/daily/2026-07-09.html`。
- 创建：`src/news_lianbo_daily/__init__.py`
  - 包标记。
- 创建：`src/news_lianbo_daily/models.py`
  - 定义日报数据结构、JSON 读取、字段校验。
- 创建：`src/news_lianbo_daily/render.py`
  - 把日报数据渲染为手机优先 HTML。
- 创建：`src/news_lianbo_daily/wecom.py`
  - 生成并发送企业微信 markdown 消息。
- 创建：`src/news_lianbo_daily/cli.py`
  - 命令行入口：校验 JSON、生成 HTML、可选发送企业微信。
- 创建：`scripts/run_daily.ps1`
  - 本地和自动化都可调用的每日执行脚本。
- 创建：`tests/test_models.py`
  - 校验数据结构和错误信息。
- 创建：`tests/test_render.py`
  - 校验 HTML 结构、中文字段、免责声明。
- 创建：`tests/test_wecom.py`
  - 校验企业微信 markdown payload，不真实发网络请求。
- 创建：`docs/自动化运行说明.md`
  - 说明如何启用 GitHub Pages、如何设置 Webhook、如何手动测试。

---

### Task 1: 项目骨架与配置

**Files:**
- Create: `.gitignore`
- Create: `.nojekyll`
- Create: `config.example.json`
- Create: `data/.gitkeep`
- Create: `daily/.gitkeep`
- Create: `src/news_lianbo_daily/__init__.py`
- Create: `docs/自动化运行说明.md`

**Interfaces:**
- Produces: 固定目录 `data/`、`daily/`，后续任务依赖这两个目录。
- Produces: 环境变量名 `WECOM_WEBHOOK_URL`，后续企业微信发送模块读取。

- [ ] **Step 1: 创建基础文件**

写入 `.gitignore`：

```gitignore
__pycache__/
*.pyc
.env
config.local.json
outputs/
work/
```

写入 `.nojekyll`，内容为空。

写入 `config.example.json`：

```json
{
  "pages_base_url": "https://1005173078g.github.io/-/",
  "wecom_webhook_env": "WECOM_WEBHOOK_URL",
  "daily_run_time": "21:30 Asia/Shanghai"
}
```

创建 `data/.gitkeep`、`daily/.gitkeep`、`src/news_lianbo_daily/__init__.py`，内容为空。

- [ ] **Step 2: 写运行说明**

写入 `docs/自动化运行说明.md`：

```markdown
# 自动化运行说明

## GitHub Pages

仓库使用 `main` 分支作为静态页面来源。每日页面保存在 `daily/YYYY-MM-DD.html`，公开链接格式为：

`https://1005173078g.github.io/-/daily/YYYY-MM-DD.html`

如果链接无法访问，请在 GitHub 仓库 Settings -> Pages 中开启 Pages，并选择 `main` 分支。

## 企业微信 Webhook

Webhook 不写入仓库。运行前在 PowerShell 设置：

```powershell
$env:WECOM_WEBHOOK_URL="你的企业微信群机器人 Webhook"
```

## 手动运行

准备 `data/YYYY-MM-DD.json` 后执行：

```powershell
python -m src.news_lianbo_daily.cli --date 2026-07-09 --send-wecom
```
```

- [ ] **Step 3: 提交**

Run:

```powershell
git add .gitignore .nojekyll config.example.json data/.gitkeep daily/.gitkeep src/news_lianbo_daily/__init__.py docs/自动化运行说明.md
git commit -m "搭建日报项目骨架"
```

Expected: commit 成功。

---

### Task 2: 日报数据模型与校验

**Files:**
- Create: `src/news_lianbo_daily/models.py`
- Create: `tests/test_models.py`

**Interfaces:**
- Produces: `Brief.from_dict(payload: dict) -> Brief`
- Produces: `Brief.load(path: str | Path) -> Brief`
- Produces: `Brief.to_page_path(daily_dir: str | Path) -> Path`
- Produces: dataclasses `Brief`、`Mainline`

- [ ] **Step 1: 写失败测试**

写入 `tests/test_models.py`：

```python
import json
import tempfile
import unittest
from pathlib import Path

from src.news_lianbo_daily.models import Brief


class BriefModelTest(unittest.TestCase):
    def sample_payload(self):
        return {
            "date": "2026-07-09",
            "title": "2026年7月9日《新闻联播》产业观察",
            "source_url": "https://tv.cctv.com/example.shtml",
            "opening": "今天主线提炼成2条，重点看政策方向和产业趋势。",
            "mainlines": [
                {
                    "name": "电子信息",
                    "tag": "高端制造",
                    "news": "电子信息制造业保持增长。",
                    "logic": "利好AI硬件、电子制造、PCB链条。",
                    "watch": ["工业富联", "立讯精密", "沪电股份"]
                },
                {
                    "name": "绿色发展",
                    "tag": "生态治理",
                    "news": "绿色发展理念持续推进。",
                    "logic": "利好生态修复、环保治理。",
                    "watch": ["瀚蓝环境", "伟明环保"]
                }
            ],
            "observation_order": ["电子信息", "绿色发展"],
            "tracking_points": ["订单兑现", "估值位置", "现金流质量"],
            "marginal_signals": ["极端高温"],
            "disclaimer": "内容仅为信息整理和学习观察，不构成投资建议。"
        }

    def test_from_dict_loads_valid_brief(self):
        brief = Brief.from_dict(self.sample_payload())
        self.assertEqual(brief.date, "2026-07-09")
        self.assertEqual(len(brief.mainlines), 2)
        self.assertEqual(brief.mainlines[0].watch, ["工业富联", "立讯精密", "沪电股份"])

    def test_requires_dynamic_mainlines_without_fixed_count(self):
        payload = self.sample_payload()
        payload["mainlines"] = payload["mainlines"][:1]
        payload["observation_order"] = ["电子信息"]
        brief = Brief.from_dict(payload)
        self.assertEqual(len(brief.mainlines), 1)

    def test_rejects_recommendation_language(self):
        payload = self.sample_payload()
        payload["mainlines"][0]["logic"] = "推荐买入相关公司。"
        with self.assertRaisesRegex(ValueError, "禁止使用投资推荐措辞"):
            Brief.from_dict(payload)

    def test_load_reads_json_file(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "2026-07-09.json"
            path.write_text(json.dumps(self.sample_payload(), ensure_ascii=False), encoding="utf-8")
            brief = Brief.load(path)
            self.assertEqual(brief.title, "2026年7月9日《新闻联播》产业观察")

    def test_page_path_uses_daily_dir(self):
        brief = Brief.from_dict(self.sample_payload())
        self.assertEqual(str(brief.to_page_path("daily")).replace("\\\\", "/"), "daily/2026-07-09.html")


if __name__ == "__main__":
    unittest.main()
```

- [ ] **Step 2: 运行测试确认失败**

Run:

```powershell
python -m unittest tests.test_models -v
```

Expected: FAIL，提示 `ModuleNotFoundError` 或 `No module named 'src.news_lianbo_daily.models'`。

- [ ] **Step 3: 实现数据模型**

写入 `src/news_lianbo_daily/models.py`：

```python
from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


FORBIDDEN_WORDS = ("推荐", "买入", "确定性机会")


@dataclass(frozen=True)
class Mainline:
    name: str
    tag: str
    news: str
    logic: str
    watch: list[str]


@dataclass(frozen=True)
class Brief:
    date: str
    title: str
    source_url: str
    opening: str
    mainlines: list[Mainline]
    observation_order: list[str]
    tracking_points: list[str]
    marginal_signals: list[str]
    disclaimer: str

    @classmethod
    def load(cls, path: str | Path) -> "Brief":
        payload = json.loads(Path(path).read_text(encoding="utf-8"))
        return cls.from_dict(payload)

    @classmethod
    def from_dict(cls, payload: dict[str, Any]) -> "Brief":
        required = [
            "date",
            "title",
            "source_url",
            "opening",
            "mainlines",
            "observation_order",
            "tracking_points",
            "marginal_signals",
            "disclaimer",
        ]
        for key in required:
            if key not in payload:
                raise ValueError(f"缺少字段：{key}")

        mainlines = [cls._mainline_from_dict(item) for item in payload["mainlines"]]
        if not mainlines:
            raise ValueError("至少需要一条主线")

        brief = cls(
            date=str(payload["date"]),
            title=str(payload["title"]),
            source_url=str(payload["source_url"]),
            opening=str(payload["opening"]),
            mainlines=mainlines,
            observation_order=[str(item) for item in payload["observation_order"]],
            tracking_points=[str(item) for item in payload["tracking_points"]],
            marginal_signals=[str(item) for item in payload["marginal_signals"]],
            disclaimer=str(payload["disclaimer"]),
        )
        brief._validate_language()
        return brief

    @staticmethod
    def _mainline_from_dict(payload: dict[str, Any]) -> Mainline:
        for key in ["name", "tag", "news", "logic", "watch"]:
            if key not in payload:
                raise ValueError(f"主线缺少字段：{key}")
        watch = [str(item) for item in payload["watch"]][:3]
        return Mainline(
            name=str(payload["name"]),
            tag=str(payload["tag"]),
            news=str(payload["news"]),
            logic=str(payload["logic"]),
            watch=watch,
        )

    def _validate_language(self) -> None:
        text_parts = [
            self.title,
            self.opening,
            self.disclaimer,
            *self.observation_order,
            *self.tracking_points,
            *self.marginal_signals,
        ]
        for mainline in self.mainlines:
            text_parts.extend([mainline.name, mainline.tag, mainline.news, mainline.logic])
            text_parts.extend(mainline.watch)
        combined = "\n".join(text_parts)
        if any(word in combined for word in FORBIDDEN_WORDS):
            raise ValueError("禁止使用投资推荐措辞")

    def to_page_path(self, daily_dir: str | Path) -> Path:
        return Path(daily_dir) / f"{self.date}.html"
```

- [ ] **Step 4: 运行测试确认通过**

Run:

```powershell
python -m unittest tests.test_models -v
```

Expected: 5 tests PASS。

- [ ] **Step 5: 提交**

```powershell
git add src/news_lianbo_daily/models.py tests/test_models.py
git commit -m "添加日报数据模型校验"
```

---

### Task 3: 手机端 HTML 渲染

**Files:**
- Create: `src/news_lianbo_daily/render.py`
- Create: `tests/test_render.py`

**Interfaces:**
- Consumes: `Brief`
- Produces: `render_html(brief: Brief) -> str`
- Produces: `write_html(brief: Brief, daily_dir: str | Path) -> Path`

- [ ] **Step 1: 写失败测试**

写入 `tests/test_render.py`：

```python
import unittest

from src.news_lianbo_daily.models import Brief
from src.news_lianbo_daily.render import render_html


class RenderHtmlTest(unittest.TestCase):
    def brief(self):
        return Brief.from_dict({
            "date": "2026-07-09",
            "title": "2026年7月9日《新闻联播》产业观察",
            "source_url": "https://tv.cctv.com/example.shtml",
            "opening": "今天主线提炼成2条，重点看产业趋势、政策方向和资金关注度。",
            "mainlines": [
                {
                    "name": "电子信息",
                    "tag": "高端制造",
                    "news": "电子信息制造业保持增长。",
                    "logic": "利好AI硬件、电子制造、PCB链条。",
                    "watch": ["工业富联", "立讯精密", "沪电股份"]
                },
                {
                    "name": "核电并网",
                    "tag": "清洁能源",
                    "news": "核电机组成功并网。",
                    "logic": "利好核电运营、核电设备、能源基建。",
                    "watch": ["中国核电", "中国广核", "东方电气"]
                }
            ],
            "observation_order": ["电子信息", "核电并网"],
            "tracking_points": ["订单兑现", "估值位置", "现金流质量"],
            "marginal_signals": ["空间载荷", "极端高温"],
            "disclaimer": "内容仅为信息整理和学习观察，不构成投资建议。"
        })

    def test_render_contains_mobile_meta_and_cards(self):
        html = render_html(self.brief())
        self.assertIn('<meta name="viewport"', html)
        self.assertIn("2026年7月9日《新闻联播》产业观察", html)
        self.assertIn("消息面", html)
        self.assertIn("逻辑", html)
        self.assertIn("观察", html)
        self.assertIn("工业富联、立讯精密、沪电股份", html)

    def test_render_contains_disclaimer_and_source(self):
        html = render_html(self.brief())
        self.assertIn("不构成投资建议", html)
        self.assertIn("央视官方来源", html)
        self.assertIn("https://tv.cctv.com/example.shtml", html)


if __name__ == "__main__":
    unittest.main()
```

- [ ] **Step 2: 运行测试确认失败**

Run:

```powershell
python -m unittest tests.test_render -v
```

Expected: FAIL，提示找不到 `render` 模块。

- [ ] **Step 3: 实现 HTML 渲染**

写入 `src/news_lianbo_daily/render.py`：

```python
from __future__ import annotations

from html import escape
from pathlib import Path

from .models import Brief


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


def _render_card(index: int, mainline) -> str:
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
```

- [ ] **Step 4: 运行测试确认通过**

Run:

```powershell
python -m unittest tests.test_render -v
```

Expected: 2 tests PASS。

- [ ] **Step 5: 提交**

```powershell
git add src/news_lianbo_daily/render.py tests/test_render.py
git commit -m "添加手机端日报渲染"
```

---

### Task 4: 企业微信消息生成与发送

**Files:**
- Create: `src/news_lianbo_daily/wecom.py`
- Create: `tests/test_wecom.py`

**Interfaces:**
- Consumes: `Brief`
- Produces: `build_markdown_payload(brief: Brief, page_url: str) -> dict`
- Produces: `send_wecom_markdown(webhook_url: str, payload: dict) -> None`

- [ ] **Step 1: 写失败测试**

写入 `tests/test_wecom.py`：

```python
import unittest

from src.news_lianbo_daily.models import Brief
from src.news_lianbo_daily.wecom import build_markdown_payload


class WeComTest(unittest.TestCase):
    def test_build_markdown_payload(self):
        brief = Brief.from_dict({
            "date": "2026-07-09",
            "title": "2026年7月9日《新闻联播》产业观察",
            "source_url": "https://tv.cctv.com/example.shtml",
            "opening": "今天主线提炼成1条。",
            "mainlines": [{
                "name": "电子信息",
                "tag": "高端制造",
                "news": "电子信息制造业保持增长。",
                "logic": "利好AI硬件。",
                "watch": ["工业富联"]
            }],
            "observation_order": ["电子信息"],
            "tracking_points": ["订单兑现"],
            "marginal_signals": ["极端高温"],
            "disclaimer": "内容仅为信息整理和学习观察，不构成投资建议。"
        })
        payload = build_markdown_payload(brief, "https://1005173078g.github.io/-/daily/2026-07-09.html")
        self.assertEqual(payload["msgtype"], "markdown")
        content = payload["markdown"]["content"]
        self.assertIn("2026年7月9日《新闻联播》产业观察", content)
        self.assertIn("主线数量：1", content)
        self.assertIn("电子信息", content)
        self.assertIn("点击查看网页版", content)


if __name__ == "__main__":
    unittest.main()
```

- [ ] **Step 2: 运行测试确认失败**

Run:

```powershell
python -m unittest tests.test_wecom -v
```

Expected: FAIL，提示找不到 `wecom` 模块。

- [ ] **Step 3: 实现企业微信模块**

写入 `src/news_lianbo_daily/wecom.py`：

```python
from __future__ import annotations

import json
from urllib import request

from .models import Brief


def build_markdown_payload(brief: Brief, page_url: str) -> dict:
    order = " > ".join(brief.observation_order)
    content = "\n".join([
        f"## {brief.title}",
        "",
        f"主线数量：{len(brief.mainlines)}",
        f"观察顺序：{order}",
        "",
        f"[点击查看网页版]({page_url})",
        "",
        "内容仅为信息整理和学习观察，不构成投资建议。"
    ])
    return {"msgtype": "markdown", "markdown": {"content": content}}


def send_wecom_markdown(webhook_url: str, payload: dict) -> None:
    data = json.dumps(payload, ensure_ascii=False).encode("utf-8")
    req = request.Request(
        webhook_url,
        data=data,
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    with request.urlopen(req, timeout=20) as response:
        body = json.loads(response.read().decode("utf-8"))
    if body.get("errcode") != 0:
        raise RuntimeError(f"企业微信发送失败：{body}")
```

- [ ] **Step 4: 运行测试确认通过**

Run:

```powershell
python -m unittest tests.test_wecom -v
```

Expected: 1 test PASS。

- [ ] **Step 5: 提交**

```powershell
git add src/news_lianbo_daily/wecom.py tests/test_wecom.py
git commit -m "添加企业微信消息发送模块"
```

---

### Task 5: 命令行入口与每日执行脚本

**Files:**
- Create: `src/news_lianbo_daily/cli.py`
- Create: `scripts/run_daily.ps1`

**Interfaces:**
- Consumes: `data/YYYY-MM-DD.json`
- Produces: `daily/YYYY-MM-DD.html`
- Produces: 可选企业微信发送行为：`--send-wecom`

- [ ] **Step 1: 实现 CLI**

写入 `src/news_lianbo_daily/cli.py`：

```python
from __future__ import annotations

import argparse
import os
from pathlib import Path

from .models import Brief
from .render import write_html
from .wecom import build_markdown_payload, send_wecom_markdown


def main() -> None:
    parser = argparse.ArgumentParser(description="生成《新闻联播》产业观察日报")
    parser.add_argument("--date", required=True, help="日期，例如 2026-07-09")
    parser.add_argument("--data-dir", default="data", help="日报 JSON 目录")
    parser.add_argument("--daily-dir", default="daily", help="HTML 输出目录")
    parser.add_argument("--pages-base-url", default="https://1005173078g.github.io/-/", help="GitHub Pages 基础地址")
    parser.add_argument("--send-wecom", action="store_true", help="生成后发送企业微信")
    args = parser.parse_args()

    data_path = Path(args.data_dir) / f"{args.date}.json"
    brief = Brief.load(data_path)
    page_path = write_html(brief, args.daily_dir)
    page_url = args.pages_base_url.rstrip("/") + "/" + page_path.as_posix()

    print(f"已生成：{page_path}")
    print(f"网页链接：{page_url}")

    if args.send_wecom:
        webhook = os.environ.get("WECOM_WEBHOOK_URL")
        if not webhook:
            raise RuntimeError("缺少环境变量 WECOM_WEBHOOK_URL")
        payload = build_markdown_payload(brief, page_url)
        send_wecom_markdown(webhook, payload)
        print("企业微信发送成功")


if __name__ == "__main__":
    main()
```

- [ ] **Step 2: 实现 PowerShell 脚本**

写入 `scripts/run_daily.ps1`：

```powershell
param(
  [string]$Date = (Get-Date -Format "yyyy-MM-dd"),
  [switch]$SendWecom
)

$ErrorActionPreference = "Stop"

if ($SendWecom) {
  python -m src.news_lianbo_daily.cli --date $Date --send-wecom
} else {
  python -m src.news_lianbo_daily.cli --date $Date
}
```

- [ ] **Step 3: 手动生成样例 JSON**

写入 `data/2026-07-09.json`：

```json
{
  "date": "2026-07-09",
  "title": "2026年7月9日《新闻联播》产业观察",
  "source_url": "https://tv.cctv.com/",
  "opening": "今天主线提炼成1条，用于验证页面生成流程。",
  "mainlines": [
    {
      "name": "电子信息",
      "tag": "高端制造",
      "news": "电子信息制造业保持增长。",
      "logic": "利好AI硬件、电子制造、PCB链条等方向。",
      "watch": ["工业富联", "立讯精密", "沪电股份"]
    }
  ],
  "observation_order": ["电子信息"],
  "tracking_points": ["订单兑现", "估值位置", "现金流质量"],
  "marginal_signals": ["极端高温"],
  "disclaimer": "内容仅为信息整理和学习观察，不构成投资建议。"
}
```

- [ ] **Step 4: 运行生成命令**

Run:

```powershell
python -m src.news_lianbo_daily.cli --date 2026-07-09
```

Expected:

```text
已生成：daily\2026-07-09.html
网页链接：https://1005173078g.github.io/-/daily/2026-07-09.html
```

- [ ] **Step 5: 运行全部测试**

Run:

```powershell
python -m unittest discover -s tests -v
```

Expected: all tests PASS。

- [ ] **Step 6: 提交**

```powershell
git add src/news_lianbo_daily/cli.py scripts/run_daily.ps1 data/2026-07-09.json daily/2026-07-09.html
git commit -m "添加日报生成命令行入口"
```

---

### Task 6: Codex 每日自动化

**Files:**
- Modify: `docs/自动化运行说明.md`

**Interfaces:**
- Consumes: GitHub 仓库当前目录。
- Consumes: 企业微信 Webhook，存于 Codex 自动化配置或本地环境变量。
- Produces: 每天 21:30 的 Codex cron 自动化。

- [ ] **Step 1: 在说明文档补充自动化提示词**

在 `docs/自动化运行说明.md` 追加：

```markdown
## Codex 每日自动化提示词

每天北京时间 21:30 运行：

1. 查找当天央视网/CCTV 官方《新闻联播》文字稿或视频页面。
2. 只基于官方来源提炼当天主线，主线数量按实际内容动态决定。
3. 把结果写入 `data/YYYY-MM-DD.json`，字段必须符合 `src/news_lianbo_daily/models.py`。
4. 执行 `python -m src.news_lianbo_daily.cli --date YYYY-MM-DD --send-wecom`。
5. 执行 `git add data/YYYY-MM-DD.json daily/YYYY-MM-DD.html`。
6. 执行 `git commit -m "生成YYYY-MM-DD新闻联播日报"`；如果没有变化则跳过提交。
7. 执行 `git push`。
8. 如果任一步失败，向企业微信群发送中文失败说明。
```

- [ ] **Step 2: 创建 Codex cron 自动化**

通过 Codex `automation_update` 创建 cron：

- name: `新闻联播企业微信日报`
- rrule: 每天 21:30，北京时间
- cwd: `C:\Users\Administrator\Documents\Codex\2026-07-09\mei`
- prompt: 使用上一步文档中的中文提示词，并包含企业微信 Webhook 的本地配置读取方式。
- model: `gpt-5.4`
- reasoningEffort: `medium`

- [ ] **Step 3: 提交说明文档**

```powershell
git add docs/自动化运行说明.md
git commit -m "补充每日自动化说明"
git push
```

---

## 自查结果

- 设计文档中的核心要求均有任务覆盖：动态主线、中文输出、HTML、企业微信、GitHub Pages、免责声明、异常说明。
- 无 `TODO`、`TBD`、`implement later` 占位。
- 模块接口一致：`Brief` 由模型任务提供，渲染和企业微信任务只消费 `Brief`。
- 计划刻意不引入第三方依赖，减少自动化运行失败面。
