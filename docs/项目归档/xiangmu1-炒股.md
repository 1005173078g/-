# xiangmu1-炒股

## 项目名称

《新闻联播》企业微信日报自动化

## 项目定位

这是一个面向股票观察的新闻联播拆解工具。每天晚上《新闻联播》播出后，自动提炼当天可形成“新闻信号 → 产业逻辑 → 观察标的”的主线，生成手机可读 HTML 页面，并通过企业微信群机器人发送链接。

## 当前能力

- 每天北京时间 21:30 自动运行。
- 使用央视网/CCTV 官方《新闻联播》内容作为来源。
- 主线数量按当天新闻实际内容动态生成，不固定条数。
- 每条主线包含 `消息面`、`逻辑`、`观察`。
- 输出 HTML 页面，适合手机浏览。
- 通过 GitHub Pages 发布网页。
- 通过企业微信群机器人发送日报链接。
- 保留免责声明：内容仅为信息整理和学习观察，不构成投资建议。

## 已实现文件

- 数据模型：`src/news_lianbo_daily/models.py`
- HTML 渲染：`src/news_lianbo_daily/render.py`
- 企业微信消息：`src/news_lianbo_daily/wecom.py`
- 命令行入口：`src/news_lianbo_daily/cli.py`
- 每日执行脚本：`scripts/run_daily.ps1`
- 自动化说明：`docs/自动化运行说明.md`
- 设计文档：`docs/superpowers/specs/2026-07-09-news-lianbo-wecom-design.md`
- 实现计划：`docs/superpowers/plans/2026-07-09-news-lianbo-wecom-implementation.md`

## 示例日报

- `daily/2026-07-08.html`
- `data/2026-07-08.json`

## 观察口径

项目只使用“观察”口径，不使用“推荐”“买入”“确定性机会”等投资推荐表达。

优先关注：

- 政策方向
- 产业趋势
- 资金关注度
- 订单兑现
- 估值位置
- 现金流质量

## 下一步

- 确认 GitHub Pages 已开启。
- 将最新代码和示例日报提交并推送到 `main`。
- 等待 2026-07-09 晚间 21:30 自动化首次正式运行。
