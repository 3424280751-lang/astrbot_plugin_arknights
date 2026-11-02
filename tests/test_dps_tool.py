"""Offline tests using only the supplied rendered fixture."""

import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
sys.path.insert(0, str(Path(__file__).resolve().parent))
from framework_stub import ensure_framework_logger

ensure_framework_logger()
from dps_tool import COLUMNS, parse_rank_html, query  # noqa: E402


class RankTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.html = Path(r"E:\GPT工作区\arkdps_fixture.html").read_text(encoding="utf-8")
        cls.rows = parse_rank_html(cls.html)

    def test_parse(self):
        self.assertEqual(len(self.rows), 278)
        self.assertEqual(list(self.rows[0]), COLUMNS)
        self.assertEqual(self.rows[0]["干员"], "新约能天使3使命必达")
        self.assertEqual(self.rows[0]["DPS"], "9999")
        self.assertEqual(self.rows[0]["总伤"], "143323")
        self.assertTrue(all(v == v.strip() for r in self.rows for v in r.values()))

    def test_candidates(self):
        result = query(self.rows, " 能 天使 ")
        self.assertGreater(len(result["candidates"]), 1)
        self.assertIsNone(result["matched"])
        self.assertGreater(
            len({r["干员"].split("3")[0] for r in result["candidates"]}), 1
        )

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


class CacheTests(unittest.IsolatedAsyncioTestCase):
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
                with patch.object(
                    dps_tool,
                    "fetch_rank_table",
                    new_callable=AsyncMock,
                    side_effect=TimeoutError,
                ):
                    result = await dps_tool.load_rows()
                    self.assertTrue(result["stale"])
                    self.assertEqual(result["rows"], rows)
                    self.assertEqual(path.read_bytes(), previous)
                    path.unlink()
                    with self.assertRaises(TimeoutError):
                        await dps_tool.load_rows()


if __name__ == "__main__":
    unittest.main()
