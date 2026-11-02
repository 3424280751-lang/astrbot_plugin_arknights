import tempfile
import unittest
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import AsyncMock

from core.cards import build_note_context
from core.operators import build_roster_context, group_operators
from core.prts import HEADERS, fetch_total, get_total, parse_total

HTML = '<div id="mw-content-text"><div data-zh="A"></div></div>'


def session(html=HTML, status=200):
    return SimpleNamespace(
        get=AsyncMock(return_value=SimpleNamespace(status_code=status, text=html))
    )


class ParseTests(unittest.TestCase):
    def test_fixture(self):
        html = (Path(__file__).parent / "fixtures/prts_list.html").read_text("utf-8")
        self.assertEqual(parse_total(html), 440)

    def test_empty_invalid_and_scope(self):
        for html in ("", "乱码", '<div data-zh="outside"></div>'):
            self.assertEqual(parse_total(html), 0)
        self.assertEqual(parse_total(HTML), 1)

    def test_override_reaches_both_cards(self):
        info = {str(i): dict(name=str(i), profession="CASTER") for i in range(401)}
        chars = [dict(charId=c) for c in info]
        roster = build_roster_context(group_operators(chars, info), info, 440)
        self.assertEqual(roster["total"], 440)
        self.assertEqual(roster["owned_percent"], 91.1)
        note = build_note_context(
            dict(chars=chars, charInfoMap=info), total_override=440
        )
        self.assertEqual(note["roster"], roster)
        self.assertEqual(build_roster_context([], info, 0)["total"], 0)


class CacheTests(unittest.IsolatedAsyncioTestCase):
    async def test_live_cache_ttl_stale_missing(self):
        with tempfile.TemporaryDirectory() as directory:
            good = session()
            self.assertEqual(await get_total(directory, good, now=0), (1, "live"))
            self.assertEqual(await get_total(directory, good, now=86399), (1, "cache"))
            self.assertEqual(good.get.await_count, 1)
            self.assertEqual(await get_total(directory, good, now=86400), (1, "live"))
            bad = session(status=403)
            self.assertEqual(await get_total(directory, bad, now=172800), (1, "stale"))
            (Path(directory) / "prts_total.json").unlink()
            self.assertEqual(await get_total(directory, bad, now=0), (None, "missing"))

    async def test_fetch_failures_and_headers(self):
        good = session()
        self.assertEqual(await fetch_total(good), 1)
        self.assertEqual(good.get.call_args.kwargs["headers"], HEADERS)
        for bad in (session(status=500), session(html=""), session()):
            if (
                bad.get.return_value.text == HTML
                and bad.get.return_value.status_code == 200
            ):
                bad.get.side_effect = TimeoutError()
            self.assertIsNone(await fetch_total(bad))

    async def test_bad_cache_and_unwritable_cache(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "prts_total.json"
            for content in (
                "{",
                '{"count":-1,"fetched_at":0}',
                '{"count":true,"fetched_at":0}',
                "[]",
            ):
                path.write_text(content, encoding="utf-8")
                self.assertEqual(
                    await get_total(directory, session(status=403), now=0),
                    (None, "missing"),
                )
            self.assertEqual(await get_total(path, session(), now=0), (1, "live"))
