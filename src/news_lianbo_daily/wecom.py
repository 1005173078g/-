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
        "内容仅为信息整理和学习观察，不构成投资建议。",
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
