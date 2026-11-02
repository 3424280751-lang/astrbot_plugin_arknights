import sys
import tempfile
import unittest
from pathlib import Path
from types import SimpleNamespace

sys.path.insert(0, str(Path(__file__).parents[1]))
sys.path.insert(0, str(Path(__file__).parent))
from framework_stub import ensure_framework_logger

ensure_framework_logger()
from core.cards import build_note_context  # noqa: E402
from core.operators import build_roster_context, group_operators  # noqa: E402
from core.render import Renderer  # noqa: E402


class CountTests(unittest.TestCase):
    def test_forms_count_once_and_missing_names_use_id(self):
        chars = [
            dict(charId=c, evolvePhase=e, equip=[dict(id="module_" + c, level=1)])
            for c, e in [
                ("amiya", 0),
                ("amiya2", 2),
                ("amiya3", 2),
                ("other", 2),
                ("unknown", 0),
            ]
        ]
        info = {
            c: dict(
                name="阿米娅" if c.startswith("amiya") else "其他干员",
                profession="CASTER",
            )
            for c in ["amiya", "amiya2", "amiya3", "other"]
        }
        info["unknown"] = dict(profession="MEDIC")
        data = dict(chars=chars, charInfoMap=info, status=dict(charCnt=99))
        note = build_note_context(data)
        self.assertEqual(note["char_count"], 3)
        self.assertEqual(note["elite2_count"], 2)
        self.assertEqual(note["module_operator_count"], 3)
        roster = build_roster_context(group_operators(chars, info), info)
        self.assertEqual(roster["owned"], 3)
        self.assertEqual(roster["total"], 3)
        self.assertEqual(roster["owned_percent"], 100.0)
        self.assertEqual(note["roster"], roster)
        self.assertEqual(
            build_note_context(dict(status=dict(charCnt=99)))["char_count"], 99
        )

    def test_total_excludes_tokens_traps_and_deduplicates_unowned_forms(self):
        info = {
            "a": dict(name="A", profession="CASTER"),
            "a2": dict(name="A", profession="WARRIOR"),
            "b": dict(name="B", profession="MEDIC"),
            "b2": dict(name="B", profession="MEDIC"),
            "c": dict(name="C", profession="TANK"),
            "token": dict(name="Token", profession="TOKEN"),
            "trap": dict(name="Trap", profession="TRAP"),
        }
        chars = [dict(charId=c) for c in ["a", "a2", "b"]]
        roster = build_roster_context(group_operators(chars, info), info)
        self.assertEqual(roster["owned"], 2)
        self.assertEqual(roster["total"], 3)
        self.assertEqual(roster["owned_percent"], 66.7)
        self.assertEqual(
            build_note_context(dict(chars=chars, charInfoMap=info))["roster"], roster
        )

    def test_zero_total(self):
        for info in [{}, {"token": dict(name="Token", profession="TOKEN")}]:
            with self.subTest(info=info):
                roster = build_roster_context([], info)
                self.assertEqual(roster["total"], 0)
                self.assertEqual(roster["owned"], 0)
                self.assertEqual(roster["owned_percent"], 0.0)


class DirectMirrorTests(unittest.IsolatedAsyncioTestCase):
    async def test_direct_rules_skip_index_and_prefer_mirror(self):
        with tempfile.TemporaryDirectory() as directory:
            renderer = Renderer(Path(directory), Path(directory) / "cache")
            for kind, path in [
                ("char_avatar", "avatars/char_002_amiya.png"),
                ("char_portrait", "portrait/char_002_amiya_2.png"),
            ]:
                filename = path.rsplit("/", 1)[1]
                urls = await renderer._public_image_candidates(
                    f"https://torappu.prts.wiki/assets/{kind}/{filename}",
                    SimpleNamespace(),
                )
                self.assertTrue(urls[0].endswith(path))
                self.assertIsNone(renderer._basename_index)


class RosterHandlerTests(unittest.IsolatedAsyncioTestCase):
    async def test_fallback_is_bounded_and_contains_summary(self):
        import ast
        from unittest.mock import AsyncMock

        source = ast.parse((Path(__file__).parents[1] / "main.py").read_text("utf-8"))
        node = next(
            n
            for n in ast.walk(source)
            if isinstance(n, ast.AsyncFunctionDef) and n.name == "show_roster"
        )
        node.decorator_list = []
        namespace = dict(
            AstrMessageEvent=object,
            group_operators=group_operators,
            build_roster_context=build_roster_context,
        )
        exec(
            compile(
                ast.fix_missing_locations(ast.Module(body=[node], type_ignores=[])),
                "main.py",
                "exec",
            ),
            namespace,
        )
        info = {
            str(i): dict(name="name" + str(i) + "x" * 30, profession="CASTER")
            for i in range(403)
        }
        data = dict(chars=[dict(charId=c) for c in info], charInfoMap=info)
        plugin = SimpleNamespace(
            _prts_total=None,
            _resolve_binding=AsyncMock(return_value=({}, {})),
            _player_data=AsyncMock(return_value=data),
            _render=AsyncMock(return_value=None),
        )
        event = SimpleNamespace(plain_result=lambda text: text)
        replies = [reply async for reply in namespace["show_roster"](plugin, event)]
        self.assertEqual(len(replies), 1)
        self.assertLessEqual(len(replies[0]), 500)
        self.assertIn("403 / 403", replies[0])
        self.assertNotIn(info["21"]["name"], replies[0])

    async def test_template_timeout_override(self):
        import ast
        import asyncio
        from unittest.mock import AsyncMock, patch

        source = ast.parse((Path(__file__).parents[1] / "main.py").read_text("utf-8"))
        node = next(
            n
            for n in ast.walk(source)
            if isinstance(n, ast.AsyncFunctionDef) and n.name == "_render"
        )
        namespace = dict(asyncio=asyncio, Path=Path, Any=object, PLUGIN_VERSION="test")
        exec(
            compile(
                ast.fix_missing_locations(ast.Module(body=[node], type_ignores=[])),
                "main.py",
                "exec",
            ),
            namespace,
        )
        plugin = SimpleNamespace(
            _renderer=SimpleNamespace(
                render_html=AsyncMock(return_value=Path("card.jpg"))
            ),
            _base_css="",
        )
        original = asyncio.wait_for
        for template, timeout in [("operator_list.html", 120), ("operator.html", 30)]:
            with patch.object(asyncio, "wait_for", wraps=original) as wait:
                await namespace["_render"](plugin, template, {})
                self.assertEqual(wait.call_args.kwargs["timeout"], timeout)


class WarmupTests(unittest.IsolatedAsyncioTestCase):
    async def test_warmup_only_avatars_and_at_most_six_downloads(self):
        import asyncio
        import re
        from unittest.mock import AsyncMock

        with tempfile.TemporaryDirectory() as directory:
            renderer = Renderer(Path(directory), Path(directory) / "cache")
            active = maximum = 0
            downloaded = []
            handler = None

            async def route(pattern, callback):
                nonlocal handler
                handler = callback

            async def download(request):
                nonlocal active, maximum
                active += 1
                maximum = max(maximum, active)
                downloaded.append(request)
                await asyncio.sleep(0.001)
                active -= 1

            async def set_content(html, **kwargs):
                await asyncio.gather(
                    *(handler(url) for url in re.findall('src="([^"]+)"', html))
                )

            page = SimpleNamespace(
                set_content=set_content,
                wait_for_function=AsyncMock(),
                evaluate=AsyncMock(return_value=0),
                close=AsyncMock(),
            )
            context = SimpleNamespace(
                route=route, new_page=AsyncMock(return_value=page), close=AsyncMock()
            )
            renderer._browser = SimpleNamespace(
                new_context=AsyncMock(return_value=context)
            )
            renderer.start = AsyncMock(return_value=True)
            renderer._cached_image_route = download
            store = SimpleNamespace(
                all_users=AsyncMock(
                    return_value={
                        "owner": dict(
                            token="test", bindings=[dict(uid="1"), dict(uid="2")]
                        )
                    }
                )
            )
            client = SimpleNamespace(
                get_authorization=AsyncMock(return_value="authorization"),
                get_credential=AsyncMock(return_value="credential"),
                get_player_info=AsyncMock(
                    return_value=dict(
                        chars=[dict(charId="char_" + str(i)) for i in range(9)]
                    )
                ),
            )
            await renderer.prewarm_avatars(store, client)
            self.assertEqual(len(downloaded), 18)
            self.assertEqual(maximum, 6)
            self.assertTrue(all("/char_avatar/" in url for url in downloaded))
            self.assertEqual(client.get_player_info.await_count, 2)
            context.close.assert_awaited_once()


class FailureCacheTests(unittest.IsolatedAsyncioTestCase):
    async def test_failed_public_asset_retries_after_five_minutes(self):
        import os
        import time
        from unittest.mock import AsyncMock

        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            route = SimpleNamespace(
                request=SimpleNamespace(
                    resource_type="image",
                    url="https://torappu.prts.wiki/assets/char_avatar/missing.png",
                ),
                fetch=AsyncMock(return_value=SimpleNamespace(status=404, headers={})),
                abort=AsyncMock(),
            )
            await Renderer(root, root / "cache")._cached_image_route(route)
            attempts = route.fetch.await_count
            self.assertGreater(attempts, 0)
            await Renderer(root, root / "cache")._cached_image_route(route)
            self.assertEqual(route.fetch.await_count, attempts)
            failure = next((root / "cache/public_assets").glob("*.failed"))
            os.utime(failure, (time.time() - 301, time.time() - 301))
            await Renderer(root, root / "cache")._cached_image_route(route)
            self.assertGreater(route.fetch.await_count, attempts)
