"""Latest stable Windows package from HiWiki's published mirror metadata."""

import asyncio
import json
import re
import time
from urllib.parse import urljoin, urlparse

import httpx

MIRROR_PAGE = (
    "https://git.hiwiki.org/zh-CN/repo/maaassistantarknights/maaassistantarknights"
)


def parse_mirror_release(page: str, payload: str) -> dict:
    """Decode Nuxt references and select the newest stable full Windows x64 ZIP.

    Args:
        page: Public repository HTML including current proxy configuration.
        payload: The public Nuxt payload referenced by that page.

    Returns:
        Version, package filename, checksum, mirror URL and source page.

    Raises:
        ValueError: If metadata or proxy rules cannot be verified.
    """
    flat = json.loads(payload)
    if not isinstance(flat, list) or len(flat) > 50000:
        raise ValueError("Unexpected mirror metadata")
    memo = {}

    def hydrate(index, depth=0):
        if depth > 30 or not isinstance(index, int) or not 0 <= index < len(flat):
            raise ValueError("Invalid payload reference")
        if index in memo:
            return memo[index]
        node = flat[index]
        if isinstance(node, dict):
            result = {key: hydrate(value, depth + 1) for key, value in node.items()}
        elif isinstance(node, list):
            if node and node[0] in ("ShallowReactive", "Reactive", "Ref", "ShallowRef"):
                result = hydrate(node[1], depth + 1)
            else:
                result = [hydrate(value, depth + 1) for value in node]
        else:
            result = node
        memo[index] = result
        return result

    data = hydrate(0)["data"]
    repo = data["repo-maaassistantarknights-maaassistantarknights-zh-CN"]["detail"]
    releases = [
        item
        for item in repo["releases"]
        if not item.get("prerelease")
        and re.fullmatch(r"v\d+\.\d+\.\d+", item.get("tag", ""))
    ]
    releases.sort(
        key=lambda item: tuple(map(int, item["tag"][1:].split("."))), reverse=True
    )
    if not releases:
        raise ValueError("No stable release found")
    release = releases[0]
    filename = f"MAA-{release['tag']}-win-x64.zip"
    asset = next(
        (item for item in release["assets"] if item.get("fileName") == filename), None
    )
    if not asset:
        raise ValueError("Latest release has no full Windows x64 package")
    origin = asset["originUrl"]
    expected = f"https://github.com/MaaAssistantArknights/MaaAssistantArknights/releases/download/{release['tag']}/{filename}"
    if origin != expected:
        raise ValueError("Unrecognized release origin")
    config = re.search(r"defaultProxyMirror:\{([^}]+)\}", page)
    if not config:
        raise ValueError("No published default mirror")
    base = re.search(r'base:"([^"]+)"', config[1])
    prefix = re.search(r'pathPrefix:"([^"]*)"', config[1])
    if not base or not prefix:
        raise ValueError("Unknown mirror URL format")
    parsed = urlparse(base[1])
    if (
        parsed.scheme != "https"
        or not parsed.hostname
        or parsed.username
        or parsed.password
    ):
        raise ValueError("Unsafe mirror address")
    url = (
        base[1].rstrip("/")
        + "/"
        + (prefix[1].strip("/") + "/" if prefix[1] else "")
        + origin.removeprefix("https://github.com/")
    )
    return {
        "version": release["tag"],
        "filename": filename,
        "url": url,
        "sha256": asset.get("sha256", ""),
        "page": MIRROR_PAGE,
    }


class MAAMirror:
    def __init__(self):
        self.lock = asyncio.Lock()
        self.cached = None
        self.expires = 0

    async def latest(self, proxy_url=""):
        """Fetch current site metadata, reusing a fresh five-minute result.

        Args:
            proxy_url: Existing optional local HTTP proxy.

        Returns:
            Verified current stable-package metadata.
        """
        async with self.lock:
            if self.cached and time.monotonic() < self.expires:
                return dict(self.cached)
            async with httpx.AsyncClient(
                timeout=18,
                follow_redirects=True,
                proxy=proxy_url or None,
                trust_env=False,
            ) as client:
                response = await client.get(MIRROR_PAGE)
                response.raise_for_status()
                if len(response.content) > 4_000_000:
                    raise ValueError("Mirror page too large")
                page = response.text
                sources = re.findall(
                    r'<script[^>]+src="([^"]+_payload\.json[^\"]*)"', page
                )
                if not sources:
                    raise ValueError("No current payload address")
                payload_url = urljoin(MIRROR_PAGE, sources[0])
                if urlparse(payload_url).netloc != "git.hiwiki.org":
                    raise ValueError("Unrecognized metadata host")
                payload = await client.get(payload_url)
                payload.raise_for_status()
                if len(payload.content) > 4_000_000:
                    raise ValueError("Mirror metadata too large")
                result = parse_mirror_release(page, payload.text)
            self.cached = result
            self.expires = time.monotonic() + 300
            return dict(result)
