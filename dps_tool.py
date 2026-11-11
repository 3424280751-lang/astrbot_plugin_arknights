"""Rendered ark-dps ranking, queries and a thirty-minute disk cache."""

import asyncio
import json
import math
import re
import time
from pathlib import Path

from astrbot.api import logger
from bs4 import BeautifulSoup

COLUMNS = "干员 DPS 总伤 质量 持续 初动 回转 部署费用 模组 DPH 攻击间隔 目标数 目标选取 用法 计算条件 计算方式 职业 上线时间 DPS排名".split()
TTL = 30 * 60
_refresh_lock = asyncio.Lock()


def add_total_rank(rows):
    """Add descending competition ranks in place.

    Args:
        rows: All ranking rows; ≥ totals use their lower bounds and nonnumeric
            totals are excluded. Original total strings are preserved.
    """
    ranked = []
    for row in rows:
        row["总伤排名"] = ""
        row["总伤可排名"] = False
        row["总伤下限"] = False
        total = str(row.get("总伤", "")).replace(",", "").strip()
        lower_bound = total.startswith("≥")
        try:
            value = float(total[1:] if lower_bound else total)
        except (TypeError, ValueError):
            continue
        if math.isfinite(value):
            row["总伤下限"] = lower_bound
            ranked.append((value, row))
    ranked.sort(key=lambda item: item[0], reverse=True)
    previous = None
    rank = 0
    for position, (value, row) in enumerate(ranked, 1):
        if value != previous:
            rank = position
        row["总伤排名"] = rank
        row["总伤可排名"] = True
        previous = value


def parse_rank_html(html: str) -> list[dict]:
    """Parse the first ranking table.

    Args:
        html: Rendered page HTML.

    Returns:
        Rows keyed by the fixed Chinese column names.

    Raises:
        ValueError: The table is missing, incomplete or too small.
    """
    table = BeautifulSoup(html, "lxml").find("table")
    if table is None or len(table.select("thead th")) < 10:
        raise ValueError("排行榜表头不足 10 列")
    rows = []
    for tr in table.select("tbody tr"):
        cells = tr.find_all("td", recursive=False)
        if not cells:
            continue
        if len(cells) != len(COLUMNS):
            raise ValueError("排行榜数据列数发生变化")
        rows.append(
            dict(
                zip(
                    COLUMNS,
                    (
                        re.sub(r"\s+", " ", td.get_text(" ", strip=True)).strip()
                        for td in cells
                    ),
                    strict=True,
                )
            )
        )
    if len(rows) < 50:
        raise ValueError("排行榜数据不足 50 行")
    add_total_rank(rows)
    return rows


async def fetch_rank_table() -> list[dict]:
    """Fetch the rendered ranking with a sixty-second timeout.

    Returns:
        Validated ranking rows.
    """
    from playwright.async_api import async_playwright

    async def scrape():
        async with async_playwright() as playwright:
            browser = await playwright.chromium.launch(headless=True)
            try:
                page = await browser.new_page()
                await page.route(
                    "**/*",
                    lambda route: (
                        route.abort()
                        if route.request.resource_type in {"image", "font", "media"}
                        else route.continue_()
                    ),
                )
                await page.goto(
                    "https://ark-dps.com/", wait_until="networkidle", timeout=50000
                )
                await page.wait_for_timeout(3000)
                return parse_rank_html(await page.content())
            finally:
                await browser.close()

    return await asyncio.wait_for(scrape(), timeout=60)


def exact_operator_rows(rows, operator: str) -> list[dict]:
    """Find rows belonging to an exact operator name.

    Args:
        rows: Parsed ranking rows.
        operator: Operator name, ignoring whitespace.

    Returns:
        Exact operator rows before skill filtering.
    """
    operator = re.sub(r"\s+", "", operator)
    exact = []
    for row in rows:
        name = re.sub(r"\s+", "", row["干员"])
        parts = re.fullmatch(r"(.*?)([123])(.*)", name)
        if operator and (parts.group(1) if parts else name) == operator:
            exact.append(row)
    return exact


def query(rows, operator: str, skill: str | None = None) -> dict:
    """Find every matching operator and optional skill without guessing.

    Args:
        rows: Parsed ranking rows.
        operator: Operator name or a name fragment.
        skill: Optional skill number or skill-name fragment.

    Returns:
        Candidates and the matched row only when exactly one remains.
    """
    operator = re.sub(r"\s+", "", operator)
    skill = re.sub(r"\s+", "", skill or "")
    if not skill:
        parts = re.fullmatch(r"(.*?)([123])", operator)
        if parts:
            operator, skill = parts.groups()
    rows = exact_operator_rows(rows, operator) or rows
    candidates = []
    for row in rows:
        name = re.sub(r"\s+", "", row["干员"])
        parts = re.fullmatch(r"(.*?)([123])(.*)", name)
        operator_name, number, skill_name = parts.groups() if parts else (name, "", "")
        if (
            operator
            and operator in operator_name
            and (
                not skill
                or (number == skill if skill.isdigit() else skill in skill_name)
            )
        ):
            candidates.append(row)
    return {
        "candidates": candidates,
        "matched": candidates[0] if len(candidates) == 1 else None,
    }


def group_by_operator(rows, operator: str) -> list[tuple[str, list[dict]]]:
    """Group matching operators, sorting skills and groups by skill number."""
    operator = re.sub(r"\s+", "", operator)
    groups = {}
    for row in query(rows, operator)["candidates"]:
        name = re.sub(r"\s+", "", row["干员"])
        parts = re.fullmatch(r"(.*?)([123])(.*)", name)
        operator_name, number, _ = parts.groups() if parts else (name, "", "")
        groups.setdefault(operator_name, []).append((int(number) if number else 4, row))
    ordered = []
    for name, skills in groups.items():
        skills.sort(key=lambda item: item[0])
        ordered.append((name, skills))
    ordered.sort(key=lambda item: item[1][0][0])
    return [(name, [row for _, row in skills]) for name, skills in ordered]


def skill_label(row) -> str:
    """Return a compact skill label, retaining unnumbered names."""
    name = re.sub(r"\s+", "", row["干员"])
    parts = re.fullmatch(r"(.*?)([123])(.*)", name)
    if parts:
        _, number, skill_name = parts.groups()
        return f"{number}技能「{skill_name}」"
    return row["干员"]


async def load_rows(force_refresh=False):
    """Read the cache or refresh once, retaining expired data on failure.

    Args:
        force_refresh: Refresh even if the cache has not expired.

    Returns:
        A dictionary containing rows, fetched_at and stale.
    """
    from astrbot.api.star import StarTools

    path = (
        Path(StarTools.get_data_dir("astrbot_plugin_arknights"))
        / "ark_dps"
        / "rank.json"
    )
    requested_at = time.time()
    async with _refresh_lock:
        cached = None
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
            if (
                isinstance(data, dict)
                and isinstance(data.get("fetched_at"), (int, float))
                and isinstance(data.get("rows"), list)
                and len(data["rows"]) >= 50
                and all(
                    isinstance(row, dict)
                    and all(isinstance(row.get(key), str) for key in COLUMNS)
                    for row in data["rows"]
                )
            ):
                add_total_rank(data["rows"])
                cached = data
        except (OSError, ValueError):
            pass
        if cached and (
            (not force_refresh and 0 <= time.time() - cached["fetched_at"] < TTL)
            or cached["fetched_at"] >= requested_at
        ):
            return {**cached, "stale": False}
        try:
            rows = await fetch_rank_table()
        except Exception as exc:
            if cached:
                logger.warning("[ark-dps] Refresh failed; using expired cache: %s", exc)
                return {**cached, "stale": True}
            raise
        data = {"fetched_at": time.time(), "rows": rows}
        try:
            path.parent.mkdir(parents=True, exist_ok=True)
            temporary = path.with_suffix(".tmp")
            temporary.write_text(json.dumps(data, ensure_ascii=False), encoding="utf-8")
            temporary.replace(path)
        except OSError as exc:
            logger.warning("[ark-dps] Failed to persist cache: %s", exc)
        return {**data, "stale": False}
