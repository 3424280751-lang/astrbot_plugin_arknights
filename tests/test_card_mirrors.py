import json
import sys
import tempfile
import unittest
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import AsyncMock

sys.path.insert(0, str(Path(__file__).parents[1]))
sys.path.insert(0, str(Path(__file__).parent))
from framework_stub import ensure_framework_logger

ensure_framework_logger()
from core.render import Renderer  # noqa: E402


class MirrorTests(unittest.IsolatedAsyncioTestCase):
    async def test_portrait_fallback_persists_under_original_url(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            url = (
                "https://torappu.prts.wiki/assets/char_portrait/char_4064_mlynar_2.png"
            )
            response = SimpleNamespace(
                status=200,
                headers={"content-type": "image/png"},
                body=AsyncMock(return_value=b"image"),
            )
            route = SimpleNamespace(
                request=SimpleNamespace(resource_type="image", url=url),
                fetch=AsyncMock(side_effect=[TimeoutError(), response]),
                fulfill=AsyncMock(),
                abort=AsyncMock(),
            )
            renderer = Renderer(root, root / "cache")
            await renderer._cached_image_route(route)
            self.assertIn(
                "/portrait/char_4064_mlynar_2.png",
                route.fetch.call_args_list[0].kwargs["url"],
            )
            self.assertEqual(route.fetch.await_count, 2)
            await Renderer(root, root / "cache")._cached_image_route(route)
            self.assertEqual(route.fetch.await_count, 2)
            route.abort.assert_not_awaited()

    async def test_basename_index_fetch_and_disk_reuse(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            payload = {
                "files": [
                    {
                        "type": "directory",
                        "name": "skill",
                        "files": [{"type": "file", "name": "icon.png"}],
                    }
                ]
            }
            response = SimpleNamespace(status=200, json=AsyncMock(return_value=payload))
            get = AsyncMock(return_value=response)
            route = SimpleNamespace(
                request=SimpleNamespace(
                    frame=SimpleNamespace(
                        page=SimpleNamespace(
                            context=SimpleNamespace(request=SimpleNamespace(get=get))
                        )
                    )
                )
            )
            url = "https://torappu.prts.wiki/assets/skill_icon/icon.png"
            first = Renderer(root, root / "cache")
            urls = await first._public_image_candidates(url, route)
            self.assertTrue(any("@main/skill/icon.png" in u for u in urls))
            index = root / "cache/public_assets/basename_index.json"
            self.assertEqual(
                json.loads(index.read_text())["icon.png"], ["skill/icon.png"]
            )
            await Renderer(root, root / "cache")._public_image_candidates(url, route)
            get.assert_awaited_once()
