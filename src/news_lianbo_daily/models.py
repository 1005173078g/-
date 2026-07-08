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
