from __future__ import annotations

import argparse
import os
from pathlib import Path

from .models import Brief
from .render import write_html
from .wecom import build_markdown_payload, send_wecom_markdown


def build_page_url(pages_base_url: str, page_path: Path) -> str:
    return pages_base_url.rstrip("/") + "/" + page_path.as_posix()


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
    page_url = build_page_url(args.pages_base_url, page_path)

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
