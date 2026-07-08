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
                    "watch": ["工业富联", "立讯精密", "沪电股份"],
                },
                {
                    "name": "核电并网",
                    "tag": "清洁能源",
                    "news": "核电机组成功并网。",
                    "logic": "利好核电运营、核电设备、能源基建。",
                    "watch": ["中国核电", "中国广核", "东方电气"],
                },
            ],
            "observation_order": ["电子信息", "核电并网"],
            "tracking_points": ["订单兑现", "估值位置", "现金流质量"],
            "marginal_signals": ["空间载荷", "极端高温"],
            "disclaimer": "内容仅为信息整理和学习观察，不构成投资建议。",
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
