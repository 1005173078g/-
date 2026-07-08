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
                "watch": ["工业富联"],
            }],
            "observation_order": ["电子信息"],
            "tracking_points": ["订单兑现"],
            "marginal_signals": ["极端高温"],
            "disclaimer": "内容仅为信息整理和学习观察，不构成投资建议。",
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
