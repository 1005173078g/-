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
                    "watch": ["工业富联", "立讯精密", "沪电股份"],
                },
                {
                    "name": "绿色发展",
                    "tag": "生态治理",
                    "news": "绿色发展理念持续推进。",
                    "logic": "利好生态修复、环保治理。",
                    "watch": ["瀚蓝环境", "伟明环保"],
                },
            ],
            "observation_order": ["电子信息", "绿色发展"],
            "tracking_points": ["订单兑现", "估值位置", "现金流质量"],
            "marginal_signals": ["极端高温"],
            "disclaimer": "内容仅为信息整理和学习观察，不构成投资建议。",
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
        self.assertEqual(str(brief.to_page_path("daily")).replace("\\", "/"), "daily/2026-07-09.html")


if __name__ == "__main__":
    unittest.main()
