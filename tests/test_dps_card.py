import ast
import asyncio
import re
import sys
import unittest
from datetime import datetime
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import AsyncMock, patch

sys.path.insert(0, str(Path(__file__).parents[1]))
sys.path.insert(0, str(Path(__file__).parent))
from framework_stub import ensure_framework_logger

ensure_framework_logger()
import dps_tool  # noqa: E402
from core.cards import build_dps_rank_context, build_note_context  # noqa: E402


def card_method():
    source = Path(__file__).parents[1] / "main.py"
    tree = ast.parse(source.read_text(encoding="utf-8"))
    node = next(
        n
        for n in ast.walk(tree)
        if isinstance(n, ast.AsyncFunctionDef) and n.name == "_dps_card"
    )
    ns = dict(
        asyncio=asyncio,
        re=re,
        datetime=datetime,
        dps_tool=dps_tool,
        build_dps_rank_context=build_dps_rank_context,
        logger=SimpleNamespace(warning=lambda *args: None),
    )
    exec(
        compile(
            ast.fix_missing_locations(ast.Module(body=[node], type_ignores=[])),
            str(source),
            "exec",
        ),
        ns,
    )
    return ns["_dps_card"]


class DPSCardTests(unittest.IsolatedAsyncioTestCase):
    async def asyncSetUp(self):
        self.rows = dps_tool.parse_rank_html(
            Path(r"E:/GPT工作区/arkdps_fixture.html").read_text(encoding="utf-8")
        )
        self.render = AsyncMock(return_value=Path("card.jpg"))
        self.harness = SimpleNamespace(_render=self.render)
        self.method = card_method()
        self.loader = patch.object(
            dps_tool,
            "load_rows",
            AsyncMock(
                return_value=dict(rows=self.rows, fetched_at=1700000000, stale=False)
            ),
        )
        self.loader.start()
        self.addCleanup(self.loader.stop)

    async def test_single_candidate_renders(self):
        image, text, title = await self.method(self.harness, "新约能天使", "3")
        self.assertEqual(image, Path("card.jpg"))
        self.assertIn("使命必达", title)
        self.render.assert_awaited_once()

    async def test_multiple_candidates_text_only(self):
        image, text, _ = await self.method(self.harness, "天使")
        self.assertIsNone(image)
        self.assertIn("多个候选", text)
        self.assertEqual(len(text.splitlines()), 8)
        self.render.assert_not_awaited()

    async def test_lower_bound_text_preserved(self):
        self.rows[0]["总伤"] = "≥110751"
        dps_tool.add_total_rank(self.rows)
        for skill, template in [("3", "dps.html"), ("", "dps_multi.html")]:
            with self.subTest(skill=skill):
                self.render.reset_mock()
                image, text, _ = await self.method(self.harness, "新约能天使", skill)
                self.assertEqual(image, Path("card.jpg"))
                self.assertIn("总伤 ≥110751", text)
                self.assertEqual(self.rows[0]["总伤"], "≥110751")
                self.render.assert_awaited_once()
                self.assertEqual(self.render.call_args.args[0], template)
        self.render.side_effect = TimeoutError()
        image, text, _ = await self.method(self.harness, "新约能天使", "3")
        self.assertIsNone(image)
        self.assertIn("总伤 ≥110751", text)

    async def test_not_found_text_only(self):
        image, text, _ = await self.method(self.harness, "不存在的干员")
        self.assertIsNone(image)
        self.assertIn("没在", text)
        self.render.assert_not_awaited()

    async def test_render_failure_keeps_numbers(self):
        self.render.side_effect = TimeoutError()
        image, text, _ = await self.method(self.harness, "新约能天使", "3")
        self.assertIsNone(image)
        self.assertIn("DPS 9999", text)

    def test_uid_precedence(self):
        self.assertEqual(
            build_note_context({"status": {"uid": "123"}}, binding_uid="456")["uid"],
            "123",
        )
        self.assertEqual(build_note_context({}, binding_uid="456")["uid"], "456")
        self.assertEqual(build_note_context({})["uid"], "未知")
