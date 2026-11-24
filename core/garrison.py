"""Garrison protocol (卫戍协议) battle-record query.

The module has two halves, mirroring ``core/gacha.py``:

* Pure mapping and context builders that shape the ``guide/resource`` and
  ``history-log`` payloads into template data. They take plain dicts so they can
  be unit tested against captured payloads.
* :class:`GarrisonClient`, which fetches the two signed endpoints through a
  :class:`~core.skland.SklandClient`.

This module never imports ``astrbot``; the display names come straight from the
payloads and the plugin's own character table.
"""

from __future__ import annotations

import asyncio
import json
import logging
import re
import time
from datetime import datetime
from pathlib import Path
from typing import Any

from .skland import Credential, SklandClient

# Display label tables, read out of the official guide tool's bundle.
MODE_LABELS = {"MULTI": "联合模拟", "SINGLE": "独立模拟", "LOCAL": "本地模拟"}
DIFFICULTY_LABELS = {
    "FUNNY": "标准模拟",
    "NORMAL": "险境模拟",
    "HARD": "绝境模拟",
    "ABYSS": "终极模拟",
}

# ``chessLevel`` is 1..6; index 0 holds the fallback for a missing level.
ROMAN = ("0", "I", "II", "III", "IV", "V", "VI", "VII", "VIII")

MAX_RECORDS = 3


class GarrisonError(Exception):
    """Raised when a garrison query cannot produce a result."""


def mode_label(value: Any) -> str:
    """Map a ``modeType`` code to its display label.

    Args:
        value: Raw ``modeType`` value.

    Returns:
        The label, the raw value when unknown, or ``"-"`` when empty.
    """
    return MODE_LABELS.get(str(value or ""), str(value or "") or "-")


def difficulty_label(value: Any) -> str:
    """Map a ``modeDifficulty`` code to its display label.

    Args:
        value: Raw ``modeDifficulty`` value.

    Returns:
        The label, the raw value when unknown, or ``"-"`` when empty.
    """
    return DIFFICULTY_LABELS.get(str(value or ""), str(value or "") or "-")


def roman_level(value: Any) -> str:
    """Render a chess level as a Roman numeral.

    Args:
        value: ``chessLevel`` value.

    Returns:
        Roman numeral clamped to the supported range, ``"0"`` when absent.
    """
    try:
        level = int(value or 0)
    except (TypeError, ValueError):
        level = 0
    return ROMAN[min(max(level, 0), len(ROMAN) - 1)]


def format_ts(value: Any) -> str:
    """Format a unix timestamp as a short local ``MM-DD HH:MM`` string.

    Args:
        value: Unix timestamp; invalid values yield ``"-"``.

    Returns:
        Formatted timestamp or ``"-"``.
    """
    try:
        return datetime.fromtimestamp(int(value)).strftime("%m-%d %H:%M")
    except (TypeError, ValueError, OSError, OverflowError):
        return "-"


def parse_count(text: str, default: int) -> int:
    """Read the first integer argument without clamping it.

    Args:
        text: Command text with optional whitespace-separated arguments.
        default: Count used when no valid integer is present.

    Returns:
        The first integer argument, or the default count.
    """
    match = re.search(r"(?<!\S)[+-]?\d+(?!\S)", text)
    try:
        return int(match.group()) if match else default
    except ValueError:
        return default


def format_short_ts(value: Any) -> str:
    """Format a local timestamp for a compact table.

    Args:
        value: Unix timestamp; invalid values yield ``"-"``.

    Returns:
        Timestamp in ``MM-DD HH:MM`` format, or ``"-"``.
    """
    return format_ts(value)


def build_maps(resource: dict[str, Any] | None) -> dict[str, dict[str, Any]]:
    """Index the guide resource so ids can be shown as names.

    Args:
        resource: The ``guide/resource`` ``data`` payload.

    Returns:
        Mapping with ``bands``, ``bonds``, ``chars`` and ``items`` keyed by id.
    """
    resource = resource or {}

    def index(items: Any, key: str) -> dict[str, dict[str, Any]]:
        out: dict[str, dict[str, Any]] = {}
        for item in items or []:
            if isinstance(item, dict) and item.get(key):
                out[str(item[key])] = item
        return out

    return {
        "bands": index(resource.get("strategies"), "strategyId"),
        "bonds": index(resource.get("bonds"), "bondId"),
        "chars": index(resource.get("chars"), "charId"),
        "items": index(resource.get("items"), "itemId"),
    }


def pick_char(maps: dict[str, Any], chess: dict[str, Any]) -> dict[str, Any]:
    """Resolve a chess piece to its portrait, Roman level and equip icons.

    ``chessInfo`` already carries ``charId`` and ``charName``; the resource only
    supplies the portrait and the equip icons.

    Args:
        maps: Indexed resource tables from :func:`build_maps`.
        chess: One ``chessSquad`` entry.

    Returns:
        Template-ready unit with ``avatar``, ``roman``, ``level`` and ``equips``.
    """
    chess = chess or {}
    info = chess.get("chessInfo") or {}
    char_id = str(info.get("charId") or chess.get("charId") or "")
    char = maps["chars"].get(char_id, {})
    equips = []
    for equip in chess.get("equips") or []:
        raw = maps["items"].get(str(equip.get("equipId") or ""), {})
        icon = str(raw.get("iconUrl") or "")
        if icon:
            equips.append({"icon": icon})
    # ``chessLevel`` comes from the payload, so treat it like ``roman_level``
    # does: a non-numeric value must not raise outside the command's guard.
    try:
        level = int(info.get("chessLevel") or 0)
    except (TypeError, ValueError):
        level = 0
    return {
        "name": str(info.get("charName") or char.get("name") or char_id),
        "avatar": str(char.get("avatarUrl") or char.get("halfBodyUrl") or ""),
        "roman": roman_level(level),
        "level": level,
        "equips": equips,
    }


def _duration(end_ts: Any, start_ts: Any) -> str:
    """Format the game duration from its unix timestamps.

    Args:
        end_ts: ``gameEndTs``.
        start_ts: ``gameStartTs``.

    Returns:
        ``"X分YY秒"``, or ``"-"`` when the timestamps are unusable.
    """
    try:
        seconds = max(0, int(end_ts or 0) - int(start_ts or 0))
    except (TypeError, ValueError):
        return "-"
    return f"{seconds // 60}分{seconds % 60:02d}秒" if seconds else "-"


def prepare_record(record: dict[str, Any], maps: dict[str, Any]) -> dict[str, Any]:
    """Shape one history record for the template.

    Args:
        record: One ``data.records`` entry.
        maps: Indexed resource tables from :func:`build_maps`.

    Returns:
        Template-ready game with badge, mode, strategy, squad, bonds and footer.
    """
    band = maps["bands"].get(str(record.get("bandId") or ""), {})
    bonds = []
    for bond in record.get("bondInfo") or []:
        raw = maps["bonds"].get(str(bond.get("bondId") or ""), {})
        bonds.append(
            {
                "name": str(raw.get("name") or bond.get("bondId") or ""),
                "icon": str(raw.get("iconUrl") or ""),
                "layer": bond.get("layer") or 0,
                "activate": bool(bond.get("activate")),
            }
        )
    bonds.sort(key=lambda item: (-item["activate"], -item["layer"]))

    squad = [pick_char(maps, chess) for chess in record.get("chessSquad") or []]
    squad.sort(key=lambda unit: -unit["level"])

    success = int(record.get("completeState") or 0) == 1
    return {
        "success": success,
        # The badge always states the outcome; the payload's ``title`` is empty
        # in practice and must never replace it.
        "title": "模拟成功" if success else "模拟失败",
        "pass_round": record.get("passRound") or 0,
        "mode": mode_label(record.get("modeType")),
        "band_icon": str(band.get("iconUrl") or ""),
        "strategy_name": str(band.get("name") or record.get("bandId") or ""),
        "difficulty": difficulty_label(record.get("modeDifficulty")),
        "version": str(record.get("versionId") or ""),
        "start": format_ts(record.get("gameStartTs")),
        "duration": _duration(record.get("gameEndTs"), record.get("gameStartTs")),
        "trophy_before": record.get("trophyBefore"),
        "trophy_after": record.get("trophyAfter"),
        "kill_cnt": record.get("killCnt"),
        "coin_cost": record.get("coinCost"),
        "squad": squad,
        "bonds": bonds,
    }


def build_user(
    player_info: dict[str, Any] | None,
    maps: dict[str, Any],
    char_names: dict[str, str] | None,
) -> dict[str, Any]:
    """Build the account header from the ``player/info`` payload.

    The assistant operator name prefers the guide resource, then falls back to
    the plugin's own character table because basic operators such as Amiya are
    absent from the guide.

    Args:
        player_info: The ``player/info`` ``data`` payload.
        maps: Indexed resource tables from :func:`build_maps`.
        char_names: ``id -> name`` table from ``core.gamedata``.

    Returns:
        Template-ready user bar.
    """
    status = (player_info or {}).get("status") or {}
    secretary = status.get("secretary") or {}
    char_id = str(secretary.get("charId") or "")
    char = maps["chars"].get(char_id, {})
    char_names = char_names or {}
    return {
        "uid": str(status.get("uid") or ""),
        "name": str(status.get("name") or ""),
        "level": status.get("level") or "",
        "avatar": (status.get("avatar") or {}).get("url") or "",
        "secretary_name": str(char.get("name") or char_names.get(char_id) or char_id),
        "secretary_icon": str(char.get("avatarUrl") or ""),
    }


def build_context(
    resource: dict[str, Any] | None,
    records: list[dict[str, Any]] | None,
    player_info: dict[str, Any] | None,
    char_names: dict[str, str] | None,
    limit: int = MAX_RECORDS,
) -> dict[str, Any]:
    """Build the template context for the recent-games card.

    Args:
        resource: The ``guide/resource`` ``data`` payload.
        records: The ``history-log`` records, newest first.
        player_info: The ``player/info`` ``data`` payload.
        char_names: ``id -> name`` table from ``core.gamedata``.
        limit: Maximum number of games to show.

    Returns:
        Context dict with ``season_name``, ``version``, ``phase_name``, ``user``
        and ``records``.
    """
    maps = build_maps(resource)
    seasons = (resource or {}).get("seasons") or []
    season = seasons[0] if seasons else {}
    version_info = (resource or {}).get("versionInfo") or {}
    records_shaped = [
        prepare_record(record, maps) for record in (records or [])[:limit]
    ]
    version = str(version_info.get("versionId") or "")
    if not version and records_shaped:
        version = str(records_shaped[0].get("version") or "")
    return {
        "season_name": str(season.get("name") or ""),
        "version": version or "-",
        "phase_name": str(version_info.get("phaseName") or ""),
        "user": build_user(player_info, maps, char_names),
        # Keyed "records" rather than "items" because Jinja resolves
        # ``garrison.items`` to the dict's own ``.items`` method.
        "records": records_shaped,
    }


def build_list_context(
    resource: dict[str, Any] | None,
    records: list[dict[str, Any]] | None,
    player_info: dict[str, Any] | None,
    char_names: dict[str, str] | None,
    limit: int = 15,
) -> dict[str, Any]:
    """Build a compact table and statistics across all available records.

    Args:
        resource: The guide resource payload.
        records: History records, newest first.
        player_info: The player information payload.
        char_names: Operator names keyed by character id.
        limit: Maximum number of rows to show.

    Returns:
        Season, user, full-history summary and ordered table rows.
    """
    records = records or []
    context = build_context(resource, records, player_info, char_names, limit)
    games = context.pop("records")
    total = len(records)
    cleared = sum(int(record.get("completeState") or 0) == 1 for record in records)
    context["summary"] = {
        "total": total,
        "shown": len(games),
        "cleared": cleared,
        "cleared_percent": f"{cleared / total * 100:.1f}" if total else "0.0",
    }
    context["rows"] = [
        {
            "start": format_short_ts(record.get("gameStartTs")),
            "difficulty": game["difficulty"].removesuffix("模拟"),
            "mode": game["mode"].removesuffix("模拟"),
            "success": game["success"],
            "trophy": (
                f"{game['trophy_before']}→{game['trophy_after']}"
                if game["success"]
                else "-"
            ),
            "rounds": game["pass_round"],
            "core_ops": "、".join(unit["name"] for unit in game["squad"][:3]) or "-",
        }
        for record, game in zip(records, games, strict=False)
    ]
    return context


def _rate(cleared: int, total: int) -> str:
    """Format ``cleared / total`` as a one-decimal percentage."""
    if total <= 0:
        return "-"
    return f"{cleared * 100 / total:.1f}"


def build_summary_context(
    resource: dict[str, Any] | None,
    records: list[dict[str, Any]] | None,
    player_info: dict[str, Any] | None,
    char_names: dict[str, str] | None,
) -> dict[str, Any]:
    """Aggregate every available garrison record into note-card stats.

    Args:
        resource: The ``guide/resource`` ``data`` payload.
        records: The ``history-log`` records, newest first.
        player_info: The ``player/info`` ``data`` payload.
        char_names: ``id -> name`` table from ``core.gamedata``.

    Returns:
        Context dict with the season header, overall counters, per-difficulty
        and per-mode breakdowns, and the covered time span.
    """
    maps = build_maps(resource)
    seasons = (resource or {}).get("seasons") or []
    season = seasons[0] if seasons else {}
    version_info = (resource or {}).get("versionInfo") or {}
    raw = list(records or [])
    rows = [prepare_record(record, maps) for record in raw]

    total = len(rows)
    cleared = sum(1 for row in rows if row["success"])
    trophies = [
        int(record.get("trophyAfter"))
        for record in raw
        if str(record.get("trophyAfter") or "").lstrip("-").isdigit()
    ]
    starts = [
        int(record.get("trophyBefore"))
        for record in raw
        if str(record.get("trophyBefore") or "").lstrip("-").isdigit()
    ]

    def bucket(key: str, order: list[str]) -> list[dict[str, Any]]:
        seen: dict[str, dict[str, Any]] = {}
        for row in rows:
            name = row[key]
            item = seen.setdefault(name, {"name": name, "total": 0, "cleared": 0})
            item["total"] += 1
            if row["success"]:
                item["cleared"] += 1
        items = list(seen.values())
        for item in items:
            item["rate"] = _rate(item["cleared"], item["total"])
        rank = {label: index for index, label in enumerate(order)}
        items.sort(key=lambda item: (rank.get(item["name"], 99), -item["total"]))
        return items

    difficulty_order = [DIFFICULTY_LABELS[key] for key in DIFFICULTY_LABELS]
    mode_order = [MODE_LABELS[key] for key in MODE_LABELS]
    stamps = sorted(
        int(record.get("gameEndTs"))
        for record in raw
        if str(record.get("gameEndTs") or "").isdigit()
    )
    first_date = format_ts(stamps[0]) if stamps else ""
    last_date = format_ts(stamps[-1]) if stamps else ""
    version = str(version_info.get("versionId") or "")
    if not version and rows:
        version = str(rows[0].get("version") or "")
    return {
        "season_name": str(season.get("name") or ""),
        "version": version or "-",
        "phase_name": str(version_info.get("phaseName") or ""),
        "user": build_user(player_info, maps, char_names),
        "total": total,
        "cleared": cleared,
        "failed": total - cleared,
        "clear_rate": _rate(cleared, total),
        "trophy_now": trophies[0] if trophies else "",
        "trophy_best": max(trophies) if trophies else "",
        "trophy_start": min(starts) if starts else "",
        "kills": sum(int(row.get("kill_cnt") or 0) for row in rows),
        "coins": sum(int(row.get("coin_cost") or 0) for row in rows),
        "by_difficulty": bucket("difficulty", difficulty_order),
        "by_mode": bucket("mode", mode_order),
        "first_date": first_date,
        "last_date": last_date,
        "span": f"{first_date} ~ {last_date}" if first_date else "-",
    }


class GarrisonClient:
    """Fetches garrison resource and history through a ``SklandClient``."""

    def __init__(self, skland: SklandClient) -> None:
        """Initialize the client.

        Args:
            skland: Shared Skland client used for the signed requests.
        """
        self.skland = skland

    async def fetch(
        self, cred: Credential, uid: str
    ) -> tuple[dict[str, Any], list[dict[str, Any]]]:
        """Fetch the guide resource and the role's recent history.

        Args:
            cred: Skland credential pair.
            uid: Role uid.

        Returns:
            Pair of the guide ``resource`` payload and the history ``records``.

        Raises:
            GarrisonError: When the guide reports no active season.
            SklandError: When a signed request fails.
        """
        resource = await self.skland.get_garrison_resource(cred)
        seasons = resource.get("seasons") or []
        season_id = str(seasons[0].get("seasonId") or "") if seasons else ""
        if not season_id:
            raise GarrisonError("未查询到卫戍协议赛季信息")
        records = await self.skland.get_garrison_history_log(cred, uid, season_id)
        return resource, records


class GarrisonTrophyRanking:
    """按 UID 缓存奖杯；重叠的群查询依次刷新并复用结果。"""

    def __init__(self, path: Path, skland: SklandClient) -> None:
        self.path = path
        self.skland = skland
        self.client = GarrisonClient(skland)
        self._lock = asyncio.Lock()

    async def rank(
        self,
        roles: dict[str, tuple[str, str]],
        own_uids: set[str],
        force: bool = False,
    ) -> dict[str, Any]:
        """返回排名行、最近成功更新时间及跳过计数。

        Args:
            roles: UID 对应的角色名和森空岛令牌。
            own_uids: 查询者的绑定角色 UID。
        """
        async with self._lock:
            try:
                cache = json.loads(self.path.read_text(encoding="utf-8"))
            except (OSError, ValueError):
                cache = {}
            if not isinstance(cache, dict):
                cache = {}
            now = int(time.time())
            semaphore = asyncio.Semaphore(4)
            refreshed = False

            async def load_role(
                uid: str, name: str, token: str
            ) -> dict[str, Any] | None:
                """读取有效缓存，或请求角色的奖杯记录。"""
                nonlocal refreshed
                entry = cache.get(uid)
                if (
                    not isinstance(entry, dict)
                    or any(
                        type(entry.get(key)) is not int
                        for key in ("trophy", "games", "last_success")
                    )
                    or force
                    or not 0 <= now - entry["last_success"] < 6 * 3600
                ):
                    async with semaphore:
                        authorization = await self.skland.get_authorization(token)
                        cred = await self.skland.get_credential(authorization)
                        _, records = await self.client.fetch(cred, uid)
                    trophies = [
                        int(value)
                        for record in records
                        if isinstance(record, dict)
                        and str(value := record.get("trophyAfter"))
                        .lstrip("-")
                        .isdecimal()
                    ]
                    if not trophies:
                        return None
                    entry = cache[uid] = {
                        "name": name,
                        "trophy": max(trophies),
                        "games": len(records),
                        "last_success": int(time.time()),
                    }
                    refreshed = True
                return {**entry, "uid": uid, "name": name, "own": uid in own_uids}

            results = await asyncio.gather(
                *(load_role(uid, *role) for uid, role in roles.items()),
                return_exceptions=True,
            )
            if refreshed:
                try:
                    self.path.parent.mkdir(parents=True, exist_ok=True)
                    temporary = self.path.with_suffix(".tmp")
                    temporary.write_text(
                        json.dumps(cache, ensure_ascii=False), encoding="utf-8"
                    )
                    temporary.replace(self.path)
                except OSError:
                    logging.getLogger(__name__).warning(
                        "Could not save garrison trophy cache"
                    )

        rows = sorted(
            (item for item in results if isinstance(item, dict)),
            key=lambda row: (-row["trophy"], row["uid"]),
        )
        previous = None
        rank = 0
        for index, row in enumerate(rows, start=1):
            if row["trophy"] != previous:
                rank, previous = index, row["trophy"]
            row["rank"] = rank
        latest = max((row["last_success"] for row in rows), default=0)
        return {
            "rows": rows,
            "entries": len(roles),
            "failed": sum(isinstance(item, BaseException) for item in results),
            "empty": results.count(None),
            "updated": datetime.fromtimestamp(latest).strftime("%Y-%m-%d %H:%M")
            if rows
            else "—",
        }
