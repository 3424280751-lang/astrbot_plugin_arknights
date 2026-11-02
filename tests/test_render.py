import asyncio
from unittest.mock import AsyncMock, Mock

import pytest
from PIL import Image

from core import render


def test_capture_is_usable_rejects_empty_file(tmp_path):
    empty = tmp_path / "empty.jpg"
    empty.write_bytes(b"")
    assert render._capture_is_usable(empty) is False


def test_capture_is_usable_accepts_non_empty_file(tmp_path):
    ok = tmp_path / "ok.jpg"
    ok.write_bytes(b"\xff\xd8\xff")
    assert render._capture_is_usable(ok) is True


def test_capture_is_usable_rejects_missing_file(tmp_path):
    assert render._capture_is_usable(tmp_path / "nope.jpg") is False


def test_max_card_px_is_conservative():
    # Above this a card is forwarded as source artwork instead of rendered.
    assert render.MAX_CARD_PX <= 30000


@pytest.mark.parametrize(
    ("height", "png_bytes", "suffix"),
    [(8000, None, ".png"), (8001, None, ".jpg"),
     (100, 5 * 1024 * 1024, ".png"),
     (100, 5 * 1024 * 1024 + 1, ".jpg")],
)
def test_render_output_format(tmp_path, monkeypatch, height, png_bytes, suffix):
    (tmp_path / "test.html").write_text("<div>test</div>", encoding="utf-8")
    renderer = render.Renderer(tmp_path, tmp_path / "cache")
    page = AsyncMock()
    page.locator = Mock(return_value=page)
    page.first = page
    page.bounding_box.return_value = {"width": 100, "height": height}
    page.evaluate.return_value = []
    page.count.return_value = 0

    async def screenshot(**kwargs):
        assert kwargs["type"] == "png"
        path = tmp_path / kwargs["path"]
        Image.new("RGBA", (100, height), (100, 120, 140, 255)).save(path, "PNG")
        if png_bytes is not None:
            with path.open("ab") as stream:
                stream.write(b"\0" * (png_bytes - path.stat().st_size))

    page.screenshot.side_effect = screenshot
    renderer.start = AsyncMock(return_value=True)
    renderer._browser = AsyncMock()
    renderer._load_card_page = AsyncMock(return_value=page)
    monkeypatch.setattr(render, "decorate_html", AsyncMock())
    output = asyncio.run(renderer.render_html("test.html", {}))
    assert output is not None
    assert output.suffix == suffix
    with Image.open(output) as image:
        assert image.format == ("JPEG" if suffix == ".jpg" else "PNG")
        assert image.size == (100, height)
    if suffix == ".jpg":
        assert output.stat().st_size < 6 * 1024 * 1024
        assert output.with_suffix(".png").exists()
