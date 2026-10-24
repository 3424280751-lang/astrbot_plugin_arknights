import asyncio
from types import SimpleNamespace

from core.render import Renderer


def test_public_asset_fallback_and_disk_cache_survive_new_renderer(tmp_path):
    async def check():
        url = "https://cdn.jsdelivr.net/gh/example/assets@main/icon.png"
        calls = []

        class Route:
            request = SimpleNamespace(resource_type="image", url=url)

            async def fetch(self, **kwargs):
                calls.append(kwargs["url"])
                if len(calls) == 1:
                    raise TimeoutError()

                async def body():
                    return b"cached-public-image"

                return SimpleNamespace(
                    status=200, headers={"content-type": "image/png"}, body=body
                )

            async def fulfill(self, **kwargs):
                self.result = kwargs

            async def abort(self):
                raise AssertionError("Valid fallback was aborted")

        first = Renderer(tmp_path, tmp_path / "cache")
        route = Route()
        await first._cached_image_route(route)
        assert len(calls) == 2
        assert (
            calls[-1]
            == "https://raw.githubusercontent.com/example/assets/main/icon.png"
        )
        second = Renderer(tmp_path, tmp_path / "cache")
        await second._cached_image_route(route)
        assert len(calls) == 2
        assert route.result["body"] == b"cached-public-image"

    asyncio.run(check())


def test_wide_artwork_fills_portrait_panel_without_shrinking_subject(tmp_path):
    async def check():
        class Image:
            async def count(self):
                return 1

            async def get_attribute(self, key):
                return "art"

            async def evaluate(self, script, style):
                self.style = style

        image = Image()

        class Box:
            async def bounding_box(self):
                return {"width": 300, "height": 600}

        page = SimpleNamespace(
            locator=lambda selector: image if selector.endswith("img") else Box()
        )
        renderer = Renderer(tmp_path, tmp_path / "cache")
        renderer._portrait_bounds["art"] = (100, 100, 1100, 1100, 1200, 1200)
        await renderer._fit_secretary_artwork(page)
        assert float(image.style["height"][:-2]) >= 600
        assert float(image.style["left"][:-2]) < 0
        assert image.style["inset"] == "auto"
        initial = float(image.style["left"][:-2])
        renderer._portrait_focus["art"] = 900
        await renderer._fit_secretary_artwork(page)
        shifted = float(image.style["left"][:-2])
        assert shifted < initial
        scale = float(image.style["width"][:-2]) / 1200
        assert shifted + 1100 * scale >= 292
        assert shifted + 100 * scale <= 8


    asyncio.run(check())
