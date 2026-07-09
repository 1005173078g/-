import json
import unittest
from unittest.mock import patch

from src.news_lianbo_daily.action_daily import (
    build_responses_payload,
    extract_response_text,
    markdown_failure_payload,
)


class ActionDailyTest(unittest.TestCase):
    def test_build_responses_payload_requires_official_source_and_json(self):
        payload = build_responses_payload("2026-07-09", "gpt-5.4-mini")
        self.assertEqual(payload["model"], "gpt-5.4-mini")
        prompt = payload["input"]
        self.assertIn("央视网/CCTV 官方", prompt)
        self.assertIn("2026-07-09", prompt)
        self.assertIn("只输出 JSON", prompt)
        self.assertIn("不构成投资建议", prompt)

    def test_extract_response_text_from_output_text(self):
        body = {"output_text": "{\"date\":\"2026-07-09\"}"}
        self.assertEqual(extract_response_text(body), "{\"date\":\"2026-07-09\"}")

    def test_extract_response_text_from_message_content(self):
        body = {
            "output": [
                {
                    "content": [
                        {"type": "output_text", "text": "{\"date\":\"2026-07-09\"}"}
                    ]
                }
            ]
        }
        self.assertEqual(extract_response_text(body), "{\"date\":\"2026-07-09\"}")

    def test_failure_payload_is_chinese_markdown(self):
        payload = markdown_failure_payload("生成失败", "官方来源暂不可用")
        self.assertEqual(payload["msgtype"], "markdown")
        content = payload["markdown"]["content"]
        self.assertIn("新闻联播日报失败", content)
        self.assertIn("生成失败", content)
        self.assertIn("官方来源暂不可用", content)

    def test_response_json_can_be_loaded_after_strip_code_fence(self):
        from src.news_lianbo_daily.action_daily import parse_brief_json

        raw = """```json
{"date":"2026-07-09","title":"标题","source_url":"https://tv.cctv.com/"}
```"""
        parsed = parse_brief_json(raw)
        self.assertEqual(parsed["date"], "2026-07-09")


if __name__ == "__main__":
    unittest.main()
