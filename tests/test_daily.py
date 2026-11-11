import ast
import time
import unittest
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import AsyncMock, patch

from jinja2 import Environment, FileSystemLoader, StrictUndefined

from core.daily import (
    build_building_context,
    build_campaign_context,
    build_recruit_context,
    build_rogue_context,
    build_task_context,
    format_duration,
    mood_value,
)

CHAR_INFO = {
    "char_002_amiya": {"name": "阿米娅", "rarity": 4, "profession": "CASTER"},
    "char_1012_skadi2": {"name": "浊心斯卡蒂", "rarity": 5, "profession": "WARRIOR"},
}


def load_tests(loader, tests, pattern):
    """Include the existing function tests in unittest discovery.

    Args:
        loader: Unittest loader.
        tests: Discovered test cases.
        pattern: Discovery filename pattern.

    Returns:
        Suite including the legacy function tests.
    """
    tests.addTests(
        unittest.FunctionTestCase(test)
        for name, test in globals().items()
        if name.startswith("test_") and callable(test)
    )
    return tests


class BuildingDurationTests(unittest.TestCase):
    def test_format_duration_boundaries(self):
        for seconds, expected in (
            (0, "0秒"),
            (1, "1秒"),
            (59, "59秒"),
            (60, "1分"),
            (61, "1分1秒"),
            (3599, "59分59秒"),
            (3600, "1小时0分"),
            (3660, "1小时1分"),
            (86399, "23小时59分"),
            (86400, "1天0小时"),
            (90000, "1天1小时"),
            (172800, "2天0小时"),
            ("60", "1分"),
            (1.9, "1秒"),
        ):
            with self.subTest(seconds=seconds):
                self.assertEqual(format_duration(seconds), expected)

    def test_format_duration_rejects_invalid_values(self):
        for seconds in (
            None,
            -1,
            -0.5,
            "-1",
            "bad",
            "",
            [],
            {},
            True,
            False,
            float("nan"),
            float("inf"),
            float("-inf"),
        ):
            with self.subTest(seconds=seconds):
                self.assertIsNone(format_duration(seconds))

    def test_training_uses_remain_secs_without_guessing_from_points(self):
        for value, seconds, text, active in (
            (3661, 3661, "1小时1分", True),
            ("60", 60, "1分", True),
            (0, 0, "0秒", False),
            (None, None, None, False),
            (-1, None, None, False),
            ("bad", None, None, False),
        ):
            with self.subTest(value=value):
                ctx = build_building_context(
                    {
                        "building": {
                            "training": {
                                "remainSecs": value,
                                "remainPoint": 26688.5,
                                "speed": 2,
                            }
                        }
                    }
                )
                self.assertEqual(ctx["training"]["remain_secs"], seconds)
                self.assertEqual(ctx["training"]["remain_text"], text)
                self.assertIs(ctx["training"]["active"], active)
        self.assertIsNone(build_building_context({})["training"]["remain_secs"])

    @patch("core.daily.time.time", return_value=1_000_000)
    def test_exchange_uses_share_complete_time_and_preserves_clue(self, clock):
        for finish, expected, text in (
            (1_003_661, 3661, "1小时1分"),
            (1_000_000, 0, "0秒"),
            (999_999, 0, "0秒"),
            (None, None, None),
            ("bad", None, None),
        ):
            with self.subTest(finish=finish):
                clue = {
                    "own": 5,
                    "received": 2,
                    "dailyReward": True,
                    "board": ["PENGUIN"],
                    "sharing": True,
                    "shareCompleteTime": finish,
                }
                ctx = build_building_context(
                    {
                        "building": {
                            "meeting": {
                                "clue": clue,
                                "completeWorkTime": 1_009_999,
                            }
                        }
                    }
                )
                self.assertEqual(
                    ctx["exchange"],
                    {
                        "share_remaining_secs": expected,
                        "share_remaining_text": text,
                        "sharing": True,
                    },
                )
                self.assertEqual(
                    ctx["clue"],
                    {
                        "own": 5,
                        "received": 2,
                        "daily_reward": True,
                        "board": ["企鹅物流"],
                        "sharing": True,
                    },
                )
                self.assertEqual(clue["shareCompleteTime"], finish)
        self.assertIs(build_building_context({})["exchange"]["sharing"], False)

    def test_recycle_absent_or_unusable_is_none(self):
        for building in (
            {},
            {"recycle": None},
            {"recycle": {}},
            {"recycles": []},
            {"recycleBin": "bad"},
        ):
            with self.subTest(building=building):
                self.assertIsNone(
                    build_building_context({"building": building})["recycle"]
                )

    def test_recycle_aliases_slots_and_optional_fields(self):
        room = {"level": 2, "chars": [{"charId": "char_002_amiya", "ap": 8640000}]}
        for key in ("recycle", "recycles", "recycleBin"):
            for slots_key in ("slots", "room"):
                for timer_key in ("remainSecs", "remain_secs"):
                    with self.subTest(key=key, slots=slots_key, timer=timer_key):
                        ctx = build_building_context(
                            {
                                "charInfoMap": CHAR_INFO,
                                "building": {
                                    key: {
                                        "level": "2",
                                        slots_key: [room],
                                        timer_key: 60,
                                        "storage": 0,
                                        "max": "10",
                                    }
                                },
                            }
                        )
                        recycle = ctx["recycle"]
                        self.assertEqual(recycle["level"], 2)
                        self.assertEqual(recycle["remain_secs"], 60)
                        self.assertEqual(recycle["remain_text"], "1分")
                        self.assertEqual((recycle["storage"], recycle["max"]), (0, 10))
                        self.assertEqual(
                            recycle["slots"][0]["operators"][0]["name"], "阿米娅"
                        )
        for raw in ({"room": room}, {"chars": room["chars"]}, [room]):
            recycle = build_building_context({"building": {"recycle": raw}})["recycle"]
            self.assertEqual(len(recycle["slots"][0]["operators"]), 1)
            self.assertIsNone(recycle["remain_secs"])
        recycle = build_building_context(
            {
                "building": {
                    "recycle": {
                        "level": "bad",
                        "slots": [None, {"level": "bad"}],
                        "remainSecs": "bad",
                        "storage": "bad",
                        "max": None,
                    }
                }
            }
        )["recycle"]
        for field in ("level", "remain_secs", "remain_text", "storage", "max"):
            self.assertIsNone(recycle[field])
        self.assertEqual(len(recycle["slots"]), 1)

    def test_template_displays_timers_and_conditionally_renders_recycle(self):
        template = Environment(
            loader=FileSystemLoader(Path(__file__).parents[1] / "templates"),
            undefined=StrictUndefined,
        ).get_template("building.html")
        for seconds, sharing in ((0, False), (None, False), (60, True)):
            with self.subTest(seconds=seconds, sharing=sharing):
                data = {
                    "building": {
                        "training": {"remainSecs": seconds},
                        "meeting": {
                            "level": 3,
                            "clue": {
                                "sharing": sharing,
                                "shareCompleteTime": 1_000_061,
                            },
                        },
                    }
                }
                with patch("core.daily.time.time", return_value=1_000_000):
                    ctx = build_building_context(data)
                html = template.render(building=ctx, base_css="", card_class="")
                self.assertIn("剩余训练时间:", html)
                self.assertIn("训练位:", html)
                self.assertIn("教官:", html)
                self.assertIn("1分" if seconds else "无训练中", html)
                self.assertIn("线索交流剩余:", html)
                self.assertIn("1分1秒" if sharing else "未在交流", html)
                self.assertNotIn("回收站", html)
        data["building"]["recycle"] = {
            "level": 2,
            "storage": 0,
            "max": 10,
            "remainSecs": 0,
            "room": {"chars": [{"charId": "char_002_amiya"}]},
        }
        data["charInfoMap"] = CHAR_INFO
        html = template.render(
            building=build_building_context(data), base_css="", card_class=""
        )
        for text in ("回收站", "Lv.2", "阿米娅", "下次产出", "0秒", "储藏空间", "0/10"):
            self.assertIn(text, html)
        del data["building"]["recycle"]["remainSecs"]
        html = template.render(
            building=build_building_context(data), base_css="", card_class=""
        )
        self.assertNotIn("下次产出", html)


class BuildingFallbackTests(unittest.IsolatedAsyncioTestCase):
    async def test_text_fallback_displays_active_idle_and_optional_recycle(self):
        source = Path(__file__).parents[1] / "main.py"
        tree = ast.parse(source.read_text(encoding="utf-8"))
        nodes = [
            node
            for node in ast.walk(tree)
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef))
            and node.name in {"show_building", "_lines"}
        ]
        for node in nodes:
            node.decorator_list = []
        namespace = {
            "build_building_context": build_building_context,
            "AstrMessageEvent": object,
        }
        exec(
            compile(ast.Module(body=nodes, type_ignores=[]), str(source), "exec"),
            namespace,
        )
        for active in (False, True):
            for has_recycle in (False, True):
                with self.subTest(active=active, has_recycle=has_recycle):
                    data = {
                        "charInfoMap": CHAR_INFO,
                        "building": {
                            "training": {"remainSecs": 60 if active else 0},
                            "meeting": {
                                "clue": {
                                    "sharing": active,
                                    "shareCompleteTime": 1_000_061,
                                }
                            },
                        },
                    }
                    if has_recycle:
                        data["building"]["recycle"] = {
                            "level": 2,
                            "remainSecs": 60,
                            "storage": 0,
                            "max": 10,
                            "chars": [{"charId": "char_002_amiya"}],
                        }
                    harness = SimpleNamespace(
                        _daily_data=AsyncMock(return_value=(data, None)),
                        _render=AsyncMock(return_value=None),
                        _lines=namespace["_lines"],
                    )
                    event = SimpleNamespace(plain_result=lambda text: text)
                    with patch("core.daily.time.time", return_value=1_000_000):
                        messages = [
                            message
                            async for message in namespace["show_building"](
                                harness, event
                            )
                        ]
                    self.assertEqual(len(messages), 1)
                    text = messages[0]
                    self.assertIn("剩余训练时间", text)
                    self.assertIn("1分" if active else "无训练中", text)
                    self.assertIn("线索交流剩余", text)
                    self.assertIn("1分1秒" if active else "未在交流", text)
                    if has_recycle:
                        for expected in (
                            "回收站",
                            "等级 2",
                            "干员 阿米娅",
                            "下次产出 1分",
                            "储藏空间 0/10",
                        ):
                            self.assertIn(expected, text)
                    else:
                        self.assertNotIn("回收站", text)

    def test_both_help_descriptions_match_spec(self):
        tree = ast.parse(
            (Path(__file__).parents[1] / "main.py").read_text(encoding="utf-8")
        )
        values = {
            node.targets[0].id: ast.literal_eval(node.value)
            for node in tree.body
            if isinstance(node, ast.Assign)
            and isinstance(node.targets[0], ast.Name)
            and node.targets[0].id in {"HELP_TEXT", "HELP_SECTIONS"}
        }
        description = "基建设施与干员心情（含训练/线索交流/回收站）"
        self.assertIn("ark基建              " + description, values["HELP_TEXT"])
        self.assertEqual(
            [
                item["desc"]
                for section in values["HELP_SECTIONS"]
                for item in section["items"]
                if item["cmd"] == "ark基建"
            ],
            [description],
        )


def test_mood_value_scales_and_clamps():
    assert mood_value(8_640_000) == 24.0
    assert mood_value(0) == 0.0
    assert mood_value(None) == 0.0
    assert mood_value("bad") == 0.0
    assert mood_value(1_800_000) == 5.0
    # never exceeds the cap
    assert mood_value(99_999_999) == 24.0


def test_build_building_context_normalizes_facilities():
    data = {
        "charInfoMap": CHAR_INFO,
        "building": {
            "powers": [
                {
                    "slotId": "s1",
                    "level": 3,
                    "chars": [
                        {"charId": "char_002_amiya", "ap": 8_640_000, "index": 0}
                    ],
                }
            ],
            "manufactures": [{"slotId": "s2", "level": 3, "chars": []}],
            "tradings": [{"slotId": "s3", "level": 2, "chars": []}],
            "dormitories": [{"slotId": "s4", "level": 5, "chars": []}],
            "control": {"slotId": "s5", "level": 5, "chars": []},
            "meeting": {
                "slotId": "s6",
                "level": 3,
                "chars": [],
                "clue": {
                    "own": 10,
                    "received": 2,
                    "dailyReward": True,
                    "sharing": False,
                    "board": ["PENGUIN", "UNKNOWN_FACTION"],
                },
            },
            "labor": {"value": 150, "maxValue": 200},
            "hire": {"level": 3, "refreshCount": 4},
            "training": {
                "level": 3,
                "trainee": {"charId": "char_1012_skadi2"},
                "trainer": {"charId": "char_002_amiya"},
            },
        },
    }
    ctx = build_building_context(data)
    names = [facility["name"] for facility in ctx["facilities"]]
    assert names == ["发电站", "制造站", "贸易站", "宿舍", "控制中枢", "会客室"]
    power = ctx["facilities"][0]
    assert power["slots"][0]["level"] == 3
    assert power["slots"][0]["operators"][0]["name"] == "阿米娅"
    assert power["slots"][0]["operators"][0]["stars"] == 5
    assert power["slots"][0]["operators"][0]["mood"] == 24.0
    assert power["slots"][0]["operators"][0]["mood_percent"] == 100
    assert ctx["labor"] == {"value": 150, "max": 200, "percent": 75}
    # known factions are translated, unknown ones are passed through
    assert ctx["clue"]["board"] == ["企鹅物流", "UNKNOWN_FACTION"]
    assert ctx["clue"]["daily_reward"] is True
    assert ctx["hire"]["refresh"] == 4
    assert ctx["training"]["trainee"] == "浊心斯卡蒂"
    assert ctx["training"]["trainer"] == "阿米娅"


def test_build_building_context_handles_empty_data():
    ctx = build_building_context({})
    assert ctx["facilities"] == []
    assert ctx["labor"]["percent"] == 0
    assert ctx["clue"]["board"] == []
    assert ctx["training"]["trainee"] == ""


def test_build_campaign_context_uses_name_maps_and_sorts():
    data = {
        "campaign": {
            "reward": {"current": 1200, "total": 1725},
            "records": [
                {"campaignId": "camp_02", "maxKills": 100},
                {"campaignId": "camp_01", "maxKills": 400},
                {"campaignId": "camp_missing", "maxKills": 250},
            ],
        },
        "campaignInfoMap": {
            "camp_01": {"name": "切尔诺伯格", "campaignZoneId": "camp_zone_3"},
            "camp_02": {"name": "龙门外环", "campaignZoneId": "camp_zone_1"},
        },
        "campaignZoneInfoMap": {
            "camp_zone_3": {"name": "乌萨斯"},
            "camp_zone_1": {"name": "炎国龙门"},
        },
    }
    ctx = build_campaign_context(data)
    assert ctx["reward"] == {"current": 1200, "total": 1725, "percent": 70}
    assert [record["name"] for record in ctx["records"]] == [
        "切尔诺伯格",
        "camp_missing",
        "龙门外环",
    ]
    assert ctx["records"][0]["zone"] == "乌萨斯"
    # unknown ids fall back to the raw id rather than disappearing
    assert ctx["records"][1]["name"] == "camp_missing"
    assert ctx["total"] == 3
    assert ctx["cleared"] == 1


def test_build_rogue_context_resolves_theme_names():
    data = {
        "rogue": {
            "records": [
                {
                    "rogueId": "rogue_1",
                    "relicCnt": 86,
                    "bank": {"current": 798, "record": 900},
                },
                {"rogueId": "rogue_2", "relicCnt": 0, "bank": {}},
            ]
        },
        "rogueInfoMap": {"rogue_1": {"name": "傀影与猩红孤钻"}},
    }
    ctx = build_rogue_context(data)
    assert ctx["themes"][0] == {
        "id": "rogue_1",
        "highest_score": None,
        "level": None,
        "highest_difficulty": None,
        "highest_from_history": False,
        "ending_difficulties": [],
        "ending_details_complete": False,
        "nodes": None,
        "clears": None,
        "name": "傀影与猩红孤钻",
        "relics": 86,
        "bank": 798,
        "bank_record": 900,
    }
    assert ctx["themes"][1]["name"] == "rogue_2"
    assert ctx["themes"][1]["bank"] == 0


def test_build_task_context():
    data = {
        "routine": {
            "daily": {"current": 8, "total": 10},
            "weekly": {"current": 5, "total": 13},
        },
        "campaign": {"reward": {"current": 300, "total": 1725}},
        "tower": {
            "reward": {
                "lowerItem": {"current": 30, "total": 60},
                "higherItem": {"current": 6, "total": 24},
                "termTs": 1700000000,
            }
        },
    }
    ctx = build_task_context(data)
    assert ctx["daily"] == {"current": 8, "total": 10, "percent": 80}
    assert ctx["weekly"]["percent"] == 38
    assert ctx["campaign"]["percent"] == 17
    assert ctx["tower_lower"]["percent"] == 50
    assert ctx["tower_higher"]["percent"] == 25
    assert ctx["tower_term"] != "未知"


def test_build_recruit_context_states():
    now = 1_000_000.0
    data = {
        "recruit": [
            {"startTs": -1, "finishTs": -1, "state": 1},
            {"startTs": 1, "finishTs": int(now + 1800), "state": 2},
            {"startTs": 1, "finishTs": int(now - 60), "state": 2},
        ]
    }
    ctx = build_recruit_context(data, now=now)
    assert [slot["state"] for slot in ctx["slots"]] == ["idle", "running", "done"]
    assert ctx["slots"][0]["state_cn"] == "空闲"
    assert ctx["slots"][1]["remaining_text"] == "30分"
    assert ctx["slots"][2]["remaining_text"] == "已完成"
    assert ctx["running"] == 1
    assert ctx["ready"] == 1


def test_build_recruit_context_empty():
    ctx = build_recruit_context({}, now=time.time())
    assert ctx["slots"] == []
    assert ctx["running"] == 0


def test_rogue_career_missing_is_not_zero():
    data = {
        "rogue": {
            "records": [{"rogueId": "rogue_2", "clearTime": 0}, {"rogueId": "rogue_1"}]
        },
        "rogueCareerMap": {"rogue_2": {"node": 0}},
    }
    themes = build_rogue_context(data)["themes"]
    assert themes[0]["nodes"] == 0 and themes[0]["clears"] == 0
    assert themes[1]["nodes"] is None and themes[1]["clears"] is None


def test_rogue_difficulty_uses_career_not_recent_runs():
    data = {
        "rogue": {"records": [{"rogueId": "rogue_5"}]},
        "rogueCareerMap": {
            "rogue_5": {
                "clearInfo": {
                    "difficulty": "请君入园",
                    "grade": 9,
                    "endings": ["ro5_ending_2"],
                    "endingGrade": {"ro5_ending_1": 5, "ro5_ending_2": 9},
                }
            }
        },
    }
    theme = build_rogue_context(data)["themes"][0]
    assert theme["highest_difficulty"] == "请君入园 9"
    assert theme["ending_difficulties"] == ["结局 1：5", "结局 2：9"]
    assert theme["ending_details_complete"] is True


def test_rogue_old_topic_does_not_invent_other_ending_grades():
    data = {
        "rogue": {"records": [{"rogueId": "rogue_2"}]},
        "rogueCareerMap": {
            "rogue_2": {
                "clearInfo": {
                    "difficulty": "波涛迭起",
                    "grade": 0,
                    "endings": ["ro2_ending_1"],
                    "endingGrade": {},
                }
            }
        },
    }
    theme = build_rogue_context(data)["themes"][0]
    assert theme["highest_difficulty"] == "波涛迭起 0"
    assert len(theme["ending_difficulties"]) == 1
    assert theme["ending_details_complete"] is False


class RogueHistoryContextTests(unittest.TestCase):
    def test_history_score_and_level_use_career_not_snapshot(self):
        for topic_id, score, level in (
            ("rogue_1", 1354, 155),
            ("rogue_4", 1887, 155),
            ("rogue_6", 2028, 108),
            ("rogue_2", 0, 0),
        ):
            with self.subTest(topic_id=topic_id):
                data = {
                    "rogue": {"records": [{"rogueId": topic_id, "bpLevel": 999}]},
                    "rogueCareerMap": {
                        topic_id: {"history": {"score": score, "bpLevel": level}}
                    },
                }
                theme = build_rogue_context(data)["themes"][0]
                self.assertEqual(theme["highest_score"], score)
                self.assertEqual(theme["level"], level)

    def test_missing_history_is_not_zero(self):
        for career in ({}, {"history": {}}, {"history": None}):
            with self.subTest(career=career):
                data = {
                    "rogue": {"records": [{"rogueId": "rogue_1", "bpLevel": 999}]},
                    "rogueCareerMap": {"rogue_1": career},
                }
                theme = build_rogue_context(data)["themes"][0]
                self.assertIsNone(theme["highest_score"])
                self.assertIsNone(theme["level"])

    def test_invalid_history_values_are_not_zero(self):
        for value in (True, False, -1, "1354", 1.5, None):
            with self.subTest(value=value):
                data = {
                    "rogue": {"records": [{"rogueId": "rogue_1"}]},
                    "rogueCareerMap": {
                        "rogue_1": {"history": {"score": value, "bpLevel": value}}
                    },
                }
                theme = build_rogue_context(data)["themes"][0]
                self.assertIsNone(theme["highest_score"])
                self.assertIsNone(theme["level"])
