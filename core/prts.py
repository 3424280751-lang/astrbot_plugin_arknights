"""PRTS operator total with a daily disk cache."""

from __future__ import annotations

import json
import math
import time
from pathlib import Path

from bs4 import BeautifulSoup

SOURCE_LABEL = "PRTS 干员一览"
URL = "https://prts.wiki/w/%E5%B9%B2%E5%91%98%E4%B8%80%E8%A7%88"
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36",
    "Accept-Language": "zh-CN,zh;q=0.9",
}


def parse_total(html: str) -> int:
    return len(
        BeautifulSoup(html, "html.parser").select("#mw-content-text div[data-zh]")
    )


async def fetch_total(session) -> int | None:
    """Fetch the operator count, returning None on HTTP or parsing failure.

    Args:
        session: An httpx-compatible asynchronous client.

    Returns:
        Positive count, or None on failure.
    """
    try:
        response = await session.get(URL, headers=HEADERS, timeout=10)
        if response.status_code == 200:
            return parse_total(response.text) or None
    except Exception:
        pass
    return None


async def get_total(
    cache_dir, session, ttl_hours=24, now=None
) -> tuple[int | None, str]:
    """Reuse a fresh count or refresh it, preserving stale data on failure.

    Args:
        cache_dir: Directory holding prts_total.json.
        session: An httpx-compatible asynchronous client.
        ttl_hours: Cache lifetime in hours.
        now: Optional Unix timestamp for deterministic checks.

    Returns:
        Count and source: live, cache, stale, or missing.
    """
    now = time.time() if now is None else now
    count = None
    try:
        path = Path(cache_dir) / "prts_total.json"
        cached = json.loads(path.read_text(encoding="utf-8"))
        value, fetched_at = cached["count"], cached["fetched_at"]
        if (
            type(value) is int
            and value > 0
            and type(fetched_at) in (int, float)
            and math.isfinite(fetched_at)
        ):
            count = value
            if 0 <= now - fetched_at < ttl_hours * 3600:
                return count, "cache"
    except Exception:
        pass
    live = await fetch_total(session)
    if live is not None:
        try:
            path = Path(cache_dir) / "prts_total.json"
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(
                json.dumps({"count": live, "fetched_at": now}), encoding="utf-8"
            )
        except Exception:
            pass
        return live, "live"
    return (count, "stale") if count is not None else (None, "missing")
