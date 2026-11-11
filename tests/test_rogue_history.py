from __future__ import annotations

import ast
import asyncio
import sys
import time
import unittest
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import AsyncMock, Mock, call

from jinja2 import Environment, FileSystemLoader, StrictUndefined

sys.path.insert(0, str(Path(__file__).parents[1]))
sys.path.insert(0, str(Path(__file__).parent))
from framework_stub import ensure_framework_logger

ensure_framework_logger()
from core.daily import build_rogue_context  # noqa: E402


def rogue_methods():
    """Load the rogue functions without starting the AstrBot plugin."""
    source = Path(__file__).parents[1] / "main.py"
    tree = ast.parse(source.read_text(encoding="utf-8"))
    wanted = {"_rogue_history", "_player_data_uncached", "show_rogue", "_lines"}
    nodes = [
        node
        for node in ast.walk(tree)
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef))
        and node.name in wanted
    ]
    for node in nodes:
        node.decorator_list = []
    namespace = {
        "asyncio": asyncio,
        "time": time,
        "logger": Mock(),
        "build_rogue_context": build_rogue_context,
    }
    exec(
        compile(ast.Module(body=nodes, type_ignores=[]), str(source), "exec"),
        namespace,
    )
    return namespace


class RogueHistoryTests(unittest.TestCase):
    def test_extracts_history_and_preserves_zero(self):
        extract = rogue_methods()["_rogue_history"]
        for score, level in ((1354, 155), (1887, 155), (2028, 108), (0, 0)):
            with self.subTest(score=score, level=level):
                self.assertEqual(
                    extract({"history": {"score": score, "bpLevel": level}}),
                    {"score": score, "bpLevel": level, "maxModeGrade": None},
                )

    def test_missing_and_invalid_values_become_none_independently(self):
        extract = rogue_methods()["_rogue_history"]
        for result in ({}, {"history": None}, {"history": {}}):
            self.assertEqual(
                extract(result),
                {"score": None, "bpLevel": None, "maxModeGrade": None},
            )
        for value in (True, False, -1, "1354", 1.5, None):
            with self.subTest(value=value):
                self.assertEqual(
                    extract({"history": {"score": value, "bpLevel": 155}}),
                    {"score": None, "bpLevel": 155, "maxModeGrade": None},
                )
                self.assertEqual(
                    extract({"history": {"score": 1354, "bpLevel": value}}),
                    {"score": 1354, "bpLevel": None, "maxModeGrade": None},
                )

    def test_max_mode_grade_ignores_invalid_values(self):
        extract = rogue_methods()["_rogue_history"]
        for grades, expected in (
            ([True, False, -1, "99", 99.5, None, 6, 9, 0], 9),
            ([True, False, -1, "99", 99.5, None], None),
            ([0], 0),
            ([], None),
        ):
            with self.subTest(grades=grades):
                result = {"history": {"records": [{"modeGrade": n} for n in grades]}}
                self.assertEqual(extract(result)["maxModeGrade"], expected)

    def test_template_displays_missing_and_zero_values(self):
        templates = Path(__file__).parents[1] / "templates"
        template = Environment(
            loader=FileSystemLoader(templates), undefined=StrictUndefined
        ).get_template("rogue.html")
        for value in (1354, 0, None):
            with self.subTest(value=value):
                data = {
                    "rogue": {"records": [{"rogueId": "rogue_1"}]},
                    "rogueCareerMap": {
                        "rogue_1": {"history": {"score": value, "bpLevel": value}}
                    },
                }
                html = template.render(
                    rogue=build_rogue_context(data), base_css="", card_class=""
                )
                expected = str(value) if value is not None else "未提供"
                for label in ("历史最高分", "当前等级"):
                    self.assertIn(
                        f'>{label}</div><div class="theme-val accent">{expected}</div>',
                        html,
                    )
                self.assertIn("投资历史最高", html)
                self.assertIn("分数与等级来自森空岛主题生涯接口，未提供不代表零", html)


class RogueDifficultyFallbackTests(unittest.TestCase):
    def test_missing_clear_info_falls_back_to_history_for_each_theme(self):
        extract = rogue_methods()["_rogue_history"]
        for topic, name in (
            ("rogue_1", "难度"),
            ("rogue_2", "波涛迭起"),
            ("rogue_3", "挑战自然"),
            ("rogue_4", "直面魂灵"),
            ("rogue_5", "请君入园"),
            ("rogue_6", "保密等级"),
            ("unknown", "难度"),
        ):
            for clear_info in (
                {},
                {"difficulty": "", "grade": 0, "endings": [], "endingGrade": {}},
            ):
                with self.subTest(topic=topic, clear_info=clear_info):
                    data = {
                        "rogue": {"records": [{"rogueId": topic}]},
                        "rogueCareerMap": {
                            topic: {
                                "clearInfo": clear_info,
                                "history": extract(
                                    {"history": {"records": [{"modeGrade": 9}]}}
                                ),
                            }
                        },
                    }
                    theme = build_rogue_context(data)["themes"][0]
                    self.assertEqual(theme["highest_difficulty"], f"{name} 9")
                    self.assertIs(theme["highest_from_history"], True)
                    self.assertEqual(theme["ending_difficulties"], [])

    def test_clear_info_takes_priority_over_higher_history_grade(self):
        for grade in (0, 13):
            with self.subTest(grade=grade):
                data = {
                    "rogue": {"records": [{"rogueId": "rogue_2"}]},
                    "rogueCareerMap": {
                        "rogue_2": {
                            "clearInfo": {
                                "difficulty": "波涛迭起",
                                "grade": grade,
                                "endings": ["ro2_ending_1"],
                                "endingGrade": {"ro2_ending_1": grade},
                            },
                            "history": {"maxModeGrade": 14},
                        }
                    },
                }
                theme = build_rogue_context(data)["themes"][0]
                self.assertEqual(theme["highest_difficulty"], f"波涛迭起 {grade}")
                self.assertIs(theme["highest_from_history"], False)
                self.assertEqual(theme["ending_difficulties"], [f"结局 1：{grade}"])

    def test_template_labels_history_and_preserves_existing_notes(self):
        template = Environment(
            loader=FileSystemLoader(Path(__file__).parents[1] / "templates"),
            undefined=StrictUndefined,
        ).get_template("rogue.html")
        for history_grade, clear_info, expected, from_history in (
            (9, {}, "难度 9（历史对局最高）", True),
            (0, {}, "难度 0（历史对局最高）", True),
            (None, {}, "未提供", False),
            (9, {"difficulty": "难度", "grade": 6}, "难度 6", False),
        ):
            with self.subTest(history_grade=history_grade, clear_info=clear_info):
                context = build_rogue_context(
                    {
                        "rogue": {"records": [{"rogueId": "rogue_1"}]},
                        "rogueCareerMap": {
                            "rogue_1": {
                                "clearInfo": clear_info,
                                "history": {"maxModeGrade": history_grade},
                            }
                        },
                    }
                )
                theme = context["themes"][0]
                self.assertIs(theme["highest_from_history"], from_history)
                if expected == "未提供":
                    self.assertIsNone(theme["highest_difficulty"])
                html = template.render(rogue=context, base_css="", card_class="")
                self.assertIn(f"最高通关难度：{expected}</strong>", html)
                if from_history:
                    self.assertIn(
                        "接口没有该主题的通关难度记录，这里取历史对局最高难度", html
                    )
                    self.assertNotIn("接口未提供各结局完整的最高难度记录", html)
                else:
                    self.assertNotIn("（历史对局最高）", html)
                    self.assertIn("接口未提供各结局完整的最高难度记录", html)

    def test_invalid_history_grade_is_not_displayed(self):
        for value in (True, False, -1, "9", 9.0, None):
            with self.subTest(value=value):
                theme = build_rogue_context(
                    {
                        "rogue": {"records": [{"rogueId": "rogue_1"}]},
                        "rogueCareerMap": {
                            "rogue_1": {"history": {"maxModeGrade": value}}
                        },
                    }
                )["themes"][0]
                self.assertIsNone(theme["highest_difficulty"])
                self.assertIs(theme["highest_from_history"], False)


class RogueHistoryHandlerTests(unittest.IsolatedAsyncioTestCase):
    async def test_existing_per_topic_requests_populate_history_and_cache(self):
        methods = rogue_methods()
        topics = ("rogue_1", "rogue_4", "rogue_6", "rogue_2")
        data = {"rogue": {"records": [{"rogueId": topic} for topic in topics]}}
        clear_info = {"grade": 9, "difficulty": "test", "endings": ["ending_1"]}
        skland = SimpleNamespace(
            get_authorization=AsyncMock(return_value="authorization"),
            get_credential=AsyncMock(return_value="credential"),
            get_player_info=AsyncMock(return_value=data),
            get_rogue_info=AsyncMock(
                side_effect=[
                    {
                        "career": {"node": 12, "clearInfo": clear_info},
                        "history": {"score": score, "bpLevel": level},
                    }
                    for score, level in ((1354, 155), (1887, 155), (2028, 108))
                ]
                + [RuntimeError("unavailable")]
            ),
        )
        harness = SimpleNamespace(config={}, _player_cache={}, skland=skland)
        fetch = methods["_player_data_uncached"]
        result = await fetch(
            harness, {"token": "token"}, {"uid": "uid"}, include_rogue=True
        )
        themes = build_rogue_context(result)["themes"]
        self.assertEqual(
            [theme["highest_score"] for theme in themes], [1354, 1887, 2028, None]
        )
        self.assertEqual([theme["level"] for theme in themes], [155, 155, 108, None])
        self.assertEqual(result["rogueCareerMap"]["rogue_1"]["node"], 12)
        self.assertEqual(result["rogueCareerMap"]["rogue_1"]["clearInfo"], clear_info)
        cached = await fetch(
            harness, {"token": "token"}, {"uid": "uid"}, include_rogue=True
        )
        self.assertIs(cached, result)
        self.assertEqual(
            skland.get_rogue_info.call_args_list,
            [call("credential", "uid", topic) for topic in topics],
        )

    async def test_text_fallback_displays_missing_and_zero_values(self):
        methods = rogue_methods()
        for value in (1354, 0, None):
            with self.subTest(value=value):
                data = {
                    "rogue": {"records": [{"rogueId": "rogue_1"}]},
                    "rogueCareerMap": {
                        "rogue_1": {"history": {"score": value, "bpLevel": value}}
                    },
                }
                harness = SimpleNamespace(
                    _daily_data=AsyncMock(return_value=(data, None)),
                    _render=AsyncMock(return_value=None),
                    _lines=methods["_lines"],
                )
                event = SimpleNamespace(plain_result=lambda text: text)
                messages = [
                    message async for message in methods["show_rogue"](harness, event)
                ]
                expected = str(value) if value is not None else "未提供"
                self.assertEqual(len(messages), 1)
                self.assertIn(f"最高分 {expected} · 等级 {expected}", messages[0])
