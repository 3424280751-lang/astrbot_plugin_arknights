"""HTML to image rendering built on Playwright and Jinja2.

Templates reference local assets with an ``__ASSET__/`` prefix, which is
resolved to a data URI before rendering so no ``file://`` resolution is needed
inside the browser. A single Chromium instance is reused across renders.

This is an independent implementation; it intentionally does not derive from the
AGPL-licensed renderers in other plugins.
"""

from __future__ import annotations

import asyncio
import base64
import hashlib
import mimetypes
import re
import time
import uuid
from pathlib import Path
from typing import Any

import jinja2
from astrbot.api import logger

from .easter_eggs import decorate_html

ASSET_PATTERN = re.compile(r"__ASSET__/([A-Za-z0-9_./-]+)")
CACHE_MAX_AGE_SECONDS = 300

# Per-card decoration themes, keyed by template file name. The renderer injects
# the class so neither the templates' call sites nor main.py has to track it.
CARD_THEMES: dict[str, str] = {
    "help.html": "t-help",
    "note.html": "t-profile",
    "sanity.html": "t-sanity",
    "operator.html": "t-operator",
    "gacha.html": "t-gacha",
    "announce.html": "t-announce",
    "announce_detail.html": "t-announce",
    "building.html": "t-building",
    "task.html": "t-task",
    "campaign.html": "t-campaign",
    "recruit.html": "t-recruit",
    "rogue.html": "t-rogue",
    "operator_list.html": "t-roster",
}

# Preferred device pixel ratio, and Chromium's hard screenshot texture limit.
DEVICE_SCALE_FACTOR = 2.0
MAX_TEXTURE_PX = 16384

# Above this a card is a narrow, multi-megabyte sliver that QQ refuses to
# upload anyway, so such announcements are sent as their original artwork
# instead of a composite card.
MAX_CARD_PX = 30000


def _capture_is_usable(path: Path) -> bool:
    """Check that a screenshot actually produced a decodable-sized file.

    Args:
        path: File the screenshot was written to.

    Returns:
        ``True`` when the file exists and is non-empty.
    """
    try:
        return path.is_file() and path.stat().st_size > 0
    except OSError:
        return False


class Renderer:
    """Render Jinja2 templates to JPEG cards."""

    def __init__(
        self,
        templates_dir: Path,
        cache_dir: Path,
        timeout_ms: int = 30000,
        proxy_url: str = "",
    ) -> None:
        """Initialize the renderer.

        Args:
            templates_dir: Directory containing the HTML templates and assets.
            cache_dir: Directory that receives the rendered images.
            timeout_ms: Per render timeout in milliseconds.
            proxy_url: Optional proxy for public image downloads.
        """
        self.templates_dir = Path(templates_dir)
        self.cache_dir = Path(cache_dir)
        self.timeout_ms = timeout_ms
        self.proxy_url = proxy_url.strip()
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        self._env = jinja2.Environment(
            loader=jinja2.FileSystemLoader(str(self.templates_dir)),
            autoescape=True,
        )
        self._lock = asyncio.Lock()
        self._playwright: Any = None
        self._browser: Any = None
        self._image_cache: dict[str, tuple[bytes, str]] = {}
        self._image_slots = asyncio.Semaphore(12)
        self._portrait_bounds: dict[str, tuple] = {}
        self._portrait_focus: dict[str, float] = {}

    async def start(self) -> bool:
        """Launch the shared browser instance.

        Returns:
            ``True`` when a browser is available, ``False`` otherwise.
        """
        async with self._lock:
            if self._browser is not None:
                return True
            try:
                from playwright.async_api import async_playwright
            except ImportError:
                logger.error("未安装 playwright，图片渲染不可用")
                return False
            try:
                self._playwright = await async_playwright().start()
                self._browser = await self._playwright.chromium.launch()
                return True
            except Exception as exc:  # noqa: BLE001 - degrade to text output
                logger.error(
                    "启动 Chromium 失败（是否已执行 playwright install chromium?）: %s",
                    exc,
                )
                await self._stop_locked()
                return False

    async def close(self) -> None:
        """Shut the browser down and release Playwright."""
        async with self._lock:
            await self._stop_locked()

    async def _stop_locked(self) -> None:
        """Tear down browser and playwright; caller must hold the lock."""
        if self._browser is not None:
            try:
                await self._browser.close()
            except Exception as exc:  # noqa: BLE001 - shutdown must not raise
                logger.debug("关闭浏览器失败: %s", exc)
            self._browser = None
        if self._playwright is not None:
            try:
                await self._playwright.stop()
            except Exception as exc:  # noqa: BLE001 - shutdown must not raise
                logger.debug("停止 playwright 失败: %s", exc)
            self._playwright = None

    def _prune_cache(self) -> None:
        """Delete rendered images older than the cache window."""
        cutoff = time.time() - CACHE_MAX_AGE_SECONDS
        try:
            for path in self.cache_dir.glob("render_*.jpg"):
                if path.stat().st_mtime < cutoff:
                    path.unlink(missing_ok=True)
        except OSError as exc:
            logger.debug("清理渲染缓存失败: %s", exc)

    def _inline_assets(self, html: str) -> str:
        """Replace ``__ASSET__/`` references with base64 data URIs.

        Args:
            html: Rendered template HTML.

        Returns:
            HTML with local asset references inlined.
        """
        root = self.templates_dir.resolve()

        def replace(match: re.Match[str]) -> str:
            candidate = (root / match.group(1)).resolve()
            if root not in candidate.parents or not candidate.is_file():
                return match.group(0)
            try:
                mime = (
                    mimetypes.guess_type(candidate.name)[0]
                    or "application/octet-stream"
                )
                encoded = base64.b64encode(candidate.read_bytes()).decode()
            except OSError as exc:
                logger.debug("内联资源失败 (%s): %s", candidate, exc)
                return match.group(0)
            return f"data:{mime};base64,{encoded}"

        return ASSET_PATTERN.sub(replace, html)

    async def _cached_image_route(self, route) -> None:
        request = route.request
        if request.resource_type != "image" or not request.url.startswith("https://"):
            await route.continue_()
            return
        cached = self._image_cache.get(request.url)
        asset_dir = self.cache_dir / "public_assets"
        public_asset = request.url.startswith(
            (
                "https://cdn.jsdelivr.net/gh/",
                "https://torappu.prts.wiki/assets/",
            )
        )
        disk = asset_dir / (hashlib.sha256(request.url.encode()).hexdigest() + ".bin")
        if not cached and public_asset and disk.is_file():
            try:
                if time.time() - disk.stat().st_mtime < 7 * 86400:
                    header, body = disk.read_bytes().split(b"\n", 1)
                    cached = (body, header.decode("ascii"))
            except (OSError, ValueError, UnicodeError):
                pass
        try:
            if cached:
                body, content_type = cached
            else:
                async with self._image_slots:
                    urls = [request.url]
                    match = re.match(
                        r"https://cdn\.jsdelivr\.net/gh/([^/]+)/([^@/]+)@([^/]+)/(.*)",
                        request.url,
                    )
                    if match:
                        owner, repo, ref, path = match.groups()
                        urls.append(
                            f"https://raw.githubusercontent.com/{owner}/{repo}/{ref}/{path}"
                        )
                    body = b""
                    for url in urls:
                        try:
                            response = await route.fetch(url=url, timeout=12000)
                            content_type = response.headers.get(
                                "content-type", "image/png"
                            ).split(";")[0]
                            if response.status == 200 and content_type.startswith(
                                "image/"
                            ):
                                body = await response.body()
                                break
                        except Exception:
                            continue
                    if not body:
                        await route.abort()
                        return
                if public_asset and len(body) <= 4_000_000:
                    try:
                        asset_dir.mkdir(exist_ok=True)
                        temporary = disk.with_suffix(f".{uuid.uuid4().hex}.tmp")
                        temporary.write_bytes(
                            content_type.encode("ascii") + b"\n" + body
                        )
                        temporary.replace(disk)
                        files = sorted(
                            asset_dir.glob("*.bin"), key=lambda f: f.stat().st_mtime
                        )
                        total = sum(f.stat().st_size for f in files)
                        while files and (len(files) > 128 or total > 64 * 1024 * 1024):
                            oldest = files.pop(0)
                            total -= oldest.stat().st_size
                            oldest.unlink(missing_ok=True)
                    except OSError:
                        pass
            if "/skin/" in request.url and request.url not in self._portrait_bounds:
                try:
                    from io import BytesIO

                    from PIL import Image as RasterImage

                    with RasterImage.open(BytesIO(body)) as portrait:
                        if portrait.width * portrait.height <= 20_000_000:
                            alpha = portrait.convert("RGBA").getchannel("A")
                            bounds = alpha.point(
                                lambda value: 255 if value > 24 else 0
                            ).getbbox()
                            if bounds:
                                self._portrait_bounds[request.url] = (
                                    *bounds,
                                    portrait.width,
                                    portrait.height,
                                )
                                left, top, right, bottom = bounds
                                solid = alpha.point(
                                    lambda value: 255 if value > 180 else 0
                                ).crop(bounds)
                                density = sum(solid.histogram()[128:]) / max(
                                    1, solid.width * solid.height
                                )
                                # Sparse artwork often has a weapon or cape pulling its
                                # canvas center away from the upper-body silhouette.
                                if density < 0.5:
                                    upper = solid.crop(
                                        (
                                            0,
                                            0,
                                            solid.width,
                                            max(1, int(solid.height * 0.15)),
                                        )
                                    ).resize((100, 20))
                                    weights = [
                                        sum(upper.getpixel((x, y)) for y in range(20))
                                        for x in range(100)
                                    ]
                                    total = sum(weights)
                                    if total:
                                        center = (
                                            sum(
                                                (x + 0.5) * value
                                                for x, value in enumerate(weights)
                                            )
                                            / total
                                            / 100
                                        )
                                        center = max(
                                            0.3, min(0.7, 0.5 + (center - 0.5) * 1.5)
                                        )
                                        self._portrait_focus[request.url] = (
                                            left + (right - left) * center
                                        )

                except Exception:
                    pass
            if len(body) <= 4_000_000:
                if len(self._image_cache) >= 256:
                    self._image_cache.pop(next(iter(self._image_cache)))
                self._image_cache[request.url] = (body, content_type)
            await route.fulfill(body=body, content_type=content_type)
        except Exception:
            try:
                await route.abort()
            except Exception:
                pass

    async def _fit_secretary_artwork(self, page) -> None:
        image = page.locator(".assistant-art img")
        if await image.count() != 1:
            return
        url = await image.get_attribute("src")
        bounds = self._portrait_bounds.get(url or "")
        box = await page.locator(".assistant-art").bounding_box()
        if not bounds or not box:
            return
        left, top, right, bottom, width, height = bounds
        # Fill the assistant panel with the visible artwork rather than shrinking
        # the character to preserve wide scenery or transparent canvas margins.
        scale = max(
            max(1, box["width"] - 16) / max(1, right - left),
            max(1, box["height"] - 16) / max(1, bottom - top),
        )
        focus = self._portrait_focus.get(url or "", (left + right) / 2)
        horizontal = max(
            box["width"] - 8 - right * scale,
            min(8 - left * scale, box["width"] / 2 - focus * scale),
        )
        style = {
            "position": "absolute",
            "inset": "auto",
            "padding": "0",
            "maxWidth": "none",
            "width": f"{width * scale}px",
            "height": f"{height * scale}px",
            "left": f"{horizontal}px",
            "top": f"{8 - top * scale}px",
        }
        await image.evaluate(
            "(element, style) => Object.assign(element.style, style)", style
        )

    async def _load_card_page(self, context, html):
        await context.route("**/*", self._cached_image_route)
        page = await context.new_page()
        await page.set_content(
            html, wait_until="domcontentloaded", timeout=self.timeout_ms
        )
        await page.evaluate(
            "() => Promise.race([Promise.all(Array.from(document.images).map(img => img.complete ? null : new Promise(resolve => { img.onload = resolve; img.onerror = resolve; }))), new Promise(resolve => setTimeout(resolve, 25000))])"
        )
        await self._fit_secretary_artwork(page)
        return page

    async def render_html(
        self, template_name: str, data: dict[str, Any]
    ) -> Path | None:
        """Render a template to a JPEG file.

        Args:
            template_name: Template filename relative to ``templates_dir``.
            data: Variables passed to the template.

        Returns:
            Path of the rendered image, or ``None`` when rendering failed. The
            caller is expected to fall back to a text reply.
        """
        try:
            # the decoration theme follows the template, so callers only supply
            # their own data
            render_data = dict(data or {})
            render_data["card_class"] = CARD_THEMES.get(template_name, "")
            html = self._inline_assets(
                self._env.get_template(template_name).render(**render_data)
            )
        except Exception as exc:  # noqa: BLE001 - template errors degrade to text
            logger.error("渲染模板 %s 失败: %s", template_name, exc)
            return None

        if not await self.start():
            return None

        self._prune_cache()
        output = self.cache_dir / f"render_{uuid.uuid4().hex[:8]}.jpg"
        page = None
        context = None
        try:
            context = await self._browser.new_context(
                device_scale_factor=DEVICE_SCALE_FACTOR,
                **({"proxy": {"server": self.proxy_url}} if self.proxy_url else {}),
                viewport={"width": 1000, "height": 800},
            )
            page = await self._load_card_page(context, html)
            # Chromium caps screenshots at 16384px of texture, so a tall page
            # rendered at 2x would be silently truncated past 8192 CSS px.
            # Measure first and drop to 1x when the page is too tall.
            box = await page.locator("body > *").first.bounding_box()
            if box and box["height"] * DEVICE_SCALE_FACTOR > MAX_TEXTURE_PX:
                logger.info(
                    "页面高度 %.0fpx 超过 %.1fx 的安全上限，降级为 1x 渲染",
                    box["height"],
                    DEVICE_SCALE_FACTOR,
                )
                await page.close()
                await context.close()
                context = await self._browser.new_context(
                    device_scale_factor=1,
                    viewport={"width": 1000, "height": 800},
                    **({"proxy": {"server": self.proxy_url}} if self.proxy_url else {}),
                )
                page = await self._load_card_page(context, html)
                box = await page.locator("body > *").first.bounding_box()
            if box and box["height"] > MAX_CARD_PX:
                logger.info(
                    "页面高度 %.0fpx 超过卡片上限 %.0fpx，改发原图",
                    box["height"],
                    MAX_CARD_PX,
                )
                return None
            if box:
                await page.set_viewport_size(
                    {"width": int(box["width"]) + 2, "height": int(box["height"]) + 2}
                )
                try:
                    await decorate_html(page)
                except Exception as exc:
                    logger.debug("Optional easter egg skipped: %s", type(exc).__name__)
                await page.screenshot(
                    path=str(output), clip=box, type="jpeg", quality=85
                )
            else:
                await page.screenshot(
                    path=str(output), full_page=True, type="jpeg", quality=85
                )
            if not _capture_is_usable(output):
                logger.error(
                    "渲染 %s 产出空文件（高度 %.0fpx），回退为文字",
                    template_name,
                    box["height"] if box else 0,
                )
                output.unlink(missing_ok=True)
                return None
            return output
        except Exception as exc:  # noqa: BLE001 - degrade to text output
            logger.error("渲染 %s 截图失败: %s", template_name, exc)
            return None
        finally:
            if page is not None:
                try:
                    await page.close()
                except Exception as exc:  # noqa: BLE001
                    logger.debug("关闭页面失败: %s", exc)
            if context is not None:
                try:
                    await context.close()
                except Exception as exc:  # noqa: BLE001
                    logger.debug("关闭上下文失败: %s", exc)
