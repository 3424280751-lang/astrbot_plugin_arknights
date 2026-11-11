"""Offline tests using only the supplied rendered fixture."""

import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
sys.path.insert(0, str(Path(__file__).resolve().parent))
from framework_stub import ensure_framework_logger

ensure_framework_logger()
from dps_tool import (  # noqa: E402
    COLUMNS,
    add_total_rank,
    exact_operator_rows,
    group_by_operator,
    parse_rank_html,
    query,
    skill_label,
)


class RankTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.html = Path(r"E:\GPT工作区\arkdps_fixture.html").read_text(encoding="utf-8")
        cls.rows = parse_rank_html(cls.html)

    def test_parse(self):
        self.assertEqual(len(self.rows), 278)
        self.assertEqual(
            list(self.rows[0]), COLUMNS + ["总伤排名", "总伤可排名", "总伤下限"]
        )
        self.assertEqual(self.rows[0]["干员"], "新约能天使3使命必达")
        self.assertEqual(self.rows[0]["DPS"], "9999")
        self.assertEqual(self.rows[0]["总伤"], "143323")
        self.assertTrue(all(r[k] == r[k].strip() for r in self.rows for k in COLUMNS))

    def test_total_rank(self):
        rows = [
            {"总伤": v}
            for v in ["80", "100", "80.0", "不适用", "—", "0", "NaN", "1,000", "inf"]
        ]
        add_total_rank(rows)
        self.assertEqual([r["总伤排名"] for r in rows], [3, 2, 3, "", "", 5, "", 1, ""])
        self.assertEqual(
            [r["总伤可排名"] for r in rows],
            [True, True, True, False, False, True, False, True, False],
        )
        add_total_rank(rows)
        self.assertEqual(rows[2]["总伤排名"], 3)

    def test_lower_bound_totals(self):
        rows = [
            {"总伤": value}
            for value in [
                "≥110751",
                "110751",
                "≥ 110,751",
                "110750",
                "不适用",
                "≥NaN",
                "≥inf",
                "≥",
                "≥≥110751",
            ]
        ]
        add_total_rank(rows)
        self.assertEqual(
            [row["总伤排名"] for row in rows], [1, 1, 1, 4, "", "", "", "", ""]
        )
        self.assertEqual(sum(row["总伤可排名"] for row in rows), 4)
        self.assertTrue(rows[0]["总伤下限"])
        self.assertFalse(rows[1]["总伤下限"])
        self.assertEqual(rows[0]["总伤"], "≥110751")
        rows[0]["总伤"] = "不适用"
        add_total_rank(rows)
        self.assertFalse(rows[0]["总伤下限"])
        self.assertFalse(rows[0]["总伤可排名"])

    def test_rosemary_ranks_and_templates(self):
        from jinja2 import Environment, FileSystemLoader

        from core.cards import build_dps_rank_context

        # Fixed population: 186 exact totals, six lower bounds and 92 excluded rows.
        values = (
            [str(200000 + i) for i in range(60)]
            + [str(60000 + i) for i in range(44)]
            + [str(10000 + i) for i in range(80)]
            + ["84341", "52318"]
            + ["≥110751", "≥124827", "≥115268", "≥65274", "≥26875", "≥38775"]
            + ["不适用"] * 92
        )
        rows = [{"总伤": value, "DPS排名": "76"} for value in values]
        add_total_rank(rows)
        self.assertEqual(len(rows), 284)
        self.assertEqual(sum(row["总伤可排名"] for row in rows), 192)
        self.assertEqual(sum(row["总伤下限"] for row in rows), 6)
        env = Environment(
            loader=FileSystemLoader(Path(__file__).resolve().parents[1] / "templates"),
            autoescape=True,
        )
        card_rows = []
        for row, expected in [(rows[184], 64), (rows[185], 110)]:
            with self.subTest(total=row["总伤"]):
                context = build_dps_rank_context(row, rows)
                self.assertEqual(context["dmg_rank"], expected)
                self.assertEqual(context["dmg_rank_total"], 192)
                self.assertEqual(context["dps_rank"], "76")
                self.assertEqual(context["dps_rank_total"], 284)
                html = env.get_template("dps.html").render(
                    dps=row, total=284, **context
                )
                self.assertIn(f"{expected} / 192", html)
                self.assertIn("76 / 284", html)
                self.assertIn(
                    "总伤排名：≥ 取下限参与，不适用不参与（全表 284 条）", html
                )
                card_rows.append(dict(row, **context))
        excluded = build_dps_rank_context(rows[-1], rows)
        self.assertEqual(excluded["dmg_rank"], "")
        self.assertEqual(excluded["dmg_rank_total"], "")
        card_rows.append(dict(rows[-1], **excluded))
        html = env.get_template("dps_multi.html").render(rows=card_rows, total=284)
        self.assertIn("64 / 192", html)
        self.assertIn("110 / 192", html)
        self.assertIn("总伤排名：≥ 取下限参与，不适用不参与（全表 284 条）", html)
        self.assertIn("总伤排名</span><b>—</b>", html)

    def test_rank_context(self):
        from core.cards import build_dps_rank_context

        rows = [{"DPS排名": "1", "总伤排名": 3, "总伤可排名": True}]
        self.assertEqual(
            build_dps_rank_context(rows[0], rows),
            {
                "dps_rank": "1",
                "dps_rank_total": 1,
                "dmg_rank": 3,
                "dmg_rank_total": 1,
            },
        )
        self.assertEqual(
            build_dps_rank_context({}, []),
            {
                "dps_rank": "",
                "dps_rank_total": "",
                "dmg_rank": "",
                "dmg_rank_total": "",
            },
        )

    def test_candidates(self):
        result = query(self.rows, " 天使 ")
        self.assertGreater(len(result["candidates"]), 1)
        self.assertIsNone(result["matched"])
        self.assertGreater(
            len({r["干员"].split("3")[0] for r in result["candidates"]}), 1
        )

    def test_exact_operator(self):
        for name in ["能天使", "新约能天使"]:
            with self.subTest(name=name):
                result = query(self.rows, f" {name} ")
                self.assertEqual(len(result["candidates"]), 3)
                self.assertIsNone(result["matched"])
                self.assertEqual(
                    result["candidates"], exact_operator_rows(self.rows, name)
                )
                groups = group_by_operator(self.rows, name)
                self.assertEqual(len(groups), 1)
                title, skills = groups[0]
                self.assertEqual(title, name)
                self.assertEqual(len(skills), 3)

    def test_exact_operator_skill(self):
        for operator, skill in [
            ("能天使", "3"),
            ("能天使 3", None),
            ("能天使3", None),
            ("能天使", "过载"),
        ]:
            with self.subTest(operator=operator, skill=skill):
                result = query(self.rows, operator, skill)
                self.assertEqual(result["matched"]["干员"], "能天使3过载模式")
        self.assertEqual(query(self.rows, "能天使", "使命")["candidates"], [])

    def test_skill(self):
        for skill in ["3", "使命必达", "使命", " 3 "]:
            with self.subTest(skill=skill):
                self.assertEqual(
                    query(self.rows, " 新约能天使 ", skill)["matched"], self.rows[0]
                )

    def test_missing(self):
        for name, skill in [
            ("不存在的干员", None),
            ("新约能天使", "不存在的技能"),
            ("", None),
            ("使命必达", None),
        ]:
            with self.subTest(name=name, skill=skill):
                self.assertEqual(
                    query(self.rows, name, skill), {"candidates": [], "matched": None}
                )

    def test_invalid(self):
        for html in ["", "<table><thead><tr><th>DPS</th></tr></thead></table>"]:
            with self.assertRaises(ValueError):
                parse_rank_html(html)

    def test_too_few_rows(self):
        from bs4 import BeautifulSoup

        soup = BeautifulSoup(self.html, "lxml")
        for tr in soup.find("table").select("tbody tr")[49:]:
            tr.decompose()
        with self.assertRaises(ValueError):
            parse_rank_html(str(soup))


class GroupTests(unittest.TestCase):
    def test_three_skills(self):
        rows = [{"干员": f"新约能天使{n}技能{n}"} for n in [3, 1, 2]]
        original = rows.copy()
        self.assertEqual(
            group_by_operator(rows, " 新约 能天使 "),
            [("新约能天使", [rows[1], rows[2], rows[0]])],
        )
        self.assertEqual(rows, original)

    def test_multiple_operators(self):
        rows = [
            {"干员": name}
            for name in ["新约能天使3使命必达", "能 天使2扫射", "新约能天使1技能"]
        ]
        self.assertEqual(
            group_by_operator(rows, "天使"),
            [("新约能天使", [rows[2], rows[0]]), ("能天使", [rows[1]])],
        )

    def test_unnumbered(self):
        rows = [{"干员": name} for name in ["能天使", "能天使3过载", "新约能天使"]]
        self.assertEqual(
            group_by_operator(rows, "能天使"),
            [("能天使", [rows[1], rows[0]])],
        )

    def test_empty(self):
        for rows, name in [
            ([], "能天使"),
            ([{"干员": "芬1冲锋"}], "能天使"),
            ([{"干员": "芬1冲锋"}], " "),
        ]:
            self.assertEqual(group_by_operator(rows, name), [])

    def test_skill_label(self):
        self.assertEqual(
            skill_label({"干员": "新约 能天使 3 使命必达"}), "3技能「使命必达」"
        )
        self.assertEqual(skill_label({"干员": " 无序号 "}), " 无序号 ")


class CacheTests(unittest.IsolatedAsyncioTestCase):
    async def test_cache_expires_after_thirty_minutes(self):
        import json
        import tempfile
        import types
        from unittest.mock import AsyncMock, patch

        import dps_tool

        now = 1_800_000_000
        rows = [{key: "0" for key in COLUMNS} for _ in range(50)]
        add_total_rank(rows)
        fresh_rows = [{**row, "DPS": "1"} for row in rows]
        with tempfile.TemporaryDirectory(
            dir=Path(__file__).resolve().parent
        ) as directory:
            star = types.ModuleType("astrbot.api.star")
            star.StarTools = types.SimpleNamespace(
                get_data_dir=lambda name: Path(directory)
            )
            path = Path(directory) / "ark_dps" / "rank.json"
            path.parent.mkdir()
            with (
                patch.dict(sys.modules, {"astrbot.api.star": star}),
                patch.object(dps_tool.time, "time", return_value=now),
            ):
                for minutes in (29, 31):
                    with self.subTest(minutes=minutes):
                        cached = {"fetched_at": now - minutes * 60, "rows": rows}
                        path.write_text(json.dumps(cached), encoding="utf-8")
                        previous = path.read_bytes()
                        with patch.object(
                            dps_tool,
                            "fetch_rank_table",
                            new_callable=AsyncMock,
                            return_value=fresh_rows,
                        ) as fetch:
                            result = await dps_tool.load_rows()
                        self.assertFalse(result["stale"])
                        if minutes == 29:
                            fetch.assert_not_awaited()
                            self.assertEqual(result, {**cached, "stale": False})
                            self.assertEqual(path.read_bytes(), previous)
                        else:
                            fetch.assert_awaited_once_with()
                            fresh = {"fetched_at": now, "rows": fresh_rows}
                            self.assertEqual(result, {**fresh, "stale": False})
                            self.assertEqual(
                                json.loads(path.read_text(encoding="utf-8")), fresh
                            )

    async def test_cache_refresh_fallback_and_single_flight(self):
        import asyncio
        import json
        import tempfile
        import time
        import types
        from unittest.mock import AsyncMock, patch

        import dps_tool

        rows = parse_rank_html(
            Path(r"E:\GPT工作区\arkdps_fixture.html").read_text(encoding="utf-8")
        )
        with tempfile.TemporaryDirectory(
            dir=Path(__file__).resolve().parent
        ) as directory:
            star = types.ModuleType("astrbot.api.star")
            star.StarTools = types.SimpleNamespace(
                get_data_dir=lambda name: Path(directory)
            )
            with patch.dict(sys.modules, {"astrbot.api.star": star}):
                with patch.object(
                    dps_tool,
                    "fetch_rank_table",
                    new_callable=AsyncMock,
                    return_value=rows,
                ) as fetch:
                    results = await asyncio.gather(
                        *(dps_tool.load_rows() for _ in range(5))
                    )
                    self.assertEqual(fetch.await_count, 1)
                    self.assertTrue(all(not r["stale"] for r in results))
                    await dps_tool.load_rows()
                    self.assertEqual(fetch.await_count, 1)
                    await dps_tool.load_rows(force_refresh=True)
                    self.assertEqual(fetch.await_count, 2)
                path = Path(directory) / "ark_dps" / "rank.json"
                path.write_text(
                    json.dumps(
                        {"fetched_at": time.time() - dps_tool.TTL - 1, "rows": rows}
                    ),
                    encoding="utf-8",
                )
                previous = path.read_bytes()
                old_rows = [{key: row[key] for key in COLUMNS} for row in rows]
                path.write_text(
                    json.dumps({"fetched_at": time.time(), "rows": old_rows}),
                    encoding="utf-8",
                )
                with patch.object(
                    dps_tool, "fetch_rank_table", new_callable=AsyncMock
                ) as fetch:
                    result = await dps_tool.load_rows()
                    self.assertEqual(result["rows"], rows)
                    fetch.assert_not_awaited()
                path.write_bytes(previous)
                error = TimeoutError("simulated refresh timeout")
                with (
                    patch.object(
                        dps_tool,
                        "fetch_rank_table",
                        new_callable=AsyncMock,
                        side_effect=error,
                    ) as fetch,
                    patch.object(dps_tool.logger, "warning") as warning,
                ):
                    result = await dps_tool.load_rows()
                    fetch.assert_awaited_once_with()
                    self.assertTrue(result["stale"])
                    self.assertEqual(result["rows"], rows)
                    self.assertEqual(
                        result["fetched_at"], json.loads(previous)["fetched_at"]
                    )
                    self.assertEqual(path.read_bytes(), previous)
                    warning.assert_called_once_with(
                        "[ark-dps] Refresh failed; using expired cache: %s", error
                    )
                    path.unlink()
                    with self.assertRaises(TimeoutError):
                        await dps_tool.load_rows()


if __name__ == "__main__":
    unittest.main()
