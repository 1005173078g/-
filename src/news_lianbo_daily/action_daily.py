from __future__ import annotations

import argparse
import json
import os
from datetime import datetime, timedelta, timezone
from pathlib import Path
from urllib import request

from .cli import build_page_url
from .models import Brief
from .render import write_html
from .wecom import build_markdown_payload, send_wecom_markdown


OPENAI_RESPONSES_URL = "https://api.openai.com/v1/responses"
DEFAULT_MODEL = "gpt-5.4-mini"
PAGES_BASE_URL = "https://1005173078g.github.io/-/"


def china_today() -> str:
    china_tz = timezone(timedelta(hours=8))
    return datetime.now(china_tz).strftime("%Y-%m-%d")


def build_responses_payload(date: str, model: str) -> dict:
    return {
        "model": model,
        "input": f"""你是中文财经新闻整理助手。请查找并只基于央视网/CCTV 官方《新闻联播》内容，生成 {date} 的产业观察日报。

硬性要求：
1. 必须优先使用央视网/CCTV 官方来源，source_url 写官方页面地址。
2. 如果找不到 {date} 官方来源，返回仍是 JSON，但 mainlines 为空，并在 opening 写明“央视官方来源暂未找到，未生成观察主线”。
3. 主线数量按当天内容动态决定，不固定为 6 条，不硬凑。
4. 每条主线必须来自新闻内容，并包含 name、tag、news、logic、watch。
5. watch 最多 3 个 A 股或港股观察标的；没有清晰产业映射时不要强行给标的。
6. 禁止使用“推荐”“买入”“确定性机会”等投资推荐措辞，统一使用“观察”。
7. disclaimer 固定为“内容仅为信息整理和学习观察，不构成投资建议。”
8. 只输出 JSON，不要输出 Markdown，不要输出解释。

JSON 字段：
{{
  "date": "{date}",
  "title": "{date}《新闻联播》产业观察",
  "source_url": "央视官方来源 URL",
  "opening": "今天主线提炼成N条，重点看……。",
  "mainlines": [
    {{
      "name": "主题名",
      "tag": "二级标签",
      "news": "消息面",
      "logic": "逻辑",
      "watch": ["标的1", "标的2", "标的3"]
    }}
  ],
  "observation_order": ["主题名1", "主题名2"],
  "tracking_points": ["订单兑现", "估值位置", "现金流质量"],
  "marginal_signals": ["边际信号1"],
  "disclaimer": "内容仅为信息整理和学习观察，不构成投资建议。"
}}""",
        "tools": [{"type": "web_search_preview"}],
    }


def call_openai_responses(api_key: str, payload: dict) -> dict:
    data = json.dumps(payload, ensure_ascii=False).encode("utf-8")
    req = request.Request(
        OPENAI_RESPONSES_URL,
        data=data,
        headers={
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
        },
        method="POST",
    )
    with request.urlopen(req, timeout=180) as response:
        return json.loads(response.read().decode("utf-8"))


def extract_response_text(body: dict) -> str:
    if body.get("output_text"):
        return str(body["output_text"]).strip()
    for item in body.get("output", []):
        for content in item.get("content", []):
            if content.get("type") == "output_text" and content.get("text"):
                return str(content["text"]).strip()
    raise ValueError("OpenAI 响应中没有可读取的文本")


def parse_brief_json(raw: str) -> dict:
    text = raw.strip()
    if text.startswith("```"):
        lines = text.splitlines()
        if lines and lines[0].startswith("```"):
            lines = lines[1:]
        if lines and lines[-1].startswith("```"):
            lines = lines[:-1]
        text = "\n".join(lines).strip()
    return json.loads(text)


def write_brief_json(payload: dict, data_dir: str | Path) -> Path:
    path = Path(data_dir) / f"{payload['date']}.json"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    return path


def markdown_failure_payload(title: str, detail: str) -> dict:
    content = "\n".join([
        "## 新闻联播日报失败",
        "",
        f"环节：{title}",
        f"原因：{detail}",
    ])
    return {"msgtype": "markdown", "markdown": {"content": content}}


def generate_daily(date: str, model: str, data_dir: str, daily_dir: str, pages_base_url: str) -> tuple[Brief, str]:
    api_key = os.environ.get("OPENAI_API_KEY")
    if not api_key:
        raise RuntimeError("缺少 GitHub Secret：OPENAI_API_KEY")

    response = call_openai_responses(api_key, build_responses_payload(date, model))
    payload = parse_brief_json(extract_response_text(response))
    write_brief_json(payload, data_dir)

    brief = Brief.from_dict(payload)
    if not brief.mainlines:
        raise RuntimeError("央视官方来源暂未找到，未生成观察主线")
    page_path = write_html(brief, daily_dir)
    return brief, build_page_url(pages_base_url, page_path)


def main() -> None:
    parser = argparse.ArgumentParser(description="GitHub Actions 生成《新闻联播》日报")
    parser.add_argument("--date", default=china_today(), help="日期，例如 2026-07-10")
    parser.add_argument("--model", default=os.environ.get("OPENAI_MODEL", DEFAULT_MODEL))
    parser.add_argument("--data-dir", default="data")
    parser.add_argument("--daily-dir", default="daily")
    parser.add_argument("--pages-base-url", default=PAGES_BASE_URL)
    parser.add_argument("--skip-wecom", action="store_true", help="只生成日报，不发送企业微信")
    args = parser.parse_args()

    webhook = os.environ.get("WECOM_WEBHOOK_URL")
    try:
        brief, page_url = generate_daily(args.date, args.model, args.data_dir, args.daily_dir, args.pages_base_url)
        if webhook and not args.skip_wecom:
            send_wecom_markdown(webhook, build_markdown_payload(brief, page_url))
            print(f"已生成并发送：{page_url}")
        else:
            print(f"已生成：{page_url}")
    except Exception as exc:
        if webhook:
            send_wecom_markdown(webhook, markdown_failure_payload("GitHub Actions 自动生成", str(exc)))
        raise


if __name__ == "__main__":
    main()
