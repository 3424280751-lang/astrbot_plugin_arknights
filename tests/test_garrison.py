"""Unit tests for the garrison (卫戍协议) record mapping and context builder."""

import ast
import asyncio
from datetime import datetime
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import AsyncMock

import pytest
from jinja2 import DictLoader, Environment, StrictUndefined

from core.garrison import (
    GarrisonClient,
    GarrisonError,
    GarrisonTrophyRanking,
    build_context,
    build_list_context,
    build_maps,
    build_user,
    difficulty_label,
    format_short_ts,
    format_ts,
    mode_label,
    parse_count,
    pick_char,
    prepare_record,
    roman_level,
)
from core.skland import Credential, SklandError
from core.templates import BASE_CSS, MACROS, TEMPLATES

RESOURCE = {
    "seasons": [
        {"seasonId": "act3autochess", "name": "规程", "phase": 0, "phaseName": ""}
    ],
    "versionInfo": {
        "seasonId": "act3autochess",
        "versionId": "V3_1",
        "phase": 1,
        "phaseName": "序列I",
    },
    "strategies": [
        {
            "strategyId": "band_weakness",
            "iconUrl": "https://example.invalid/band_weakness.png",
            "initiatorName": "陈",
            "name": "以己之长",
        }
    ],
    "bonds": [
        {
            "bondId": "yanShip",
            "iconUrl": "https://example.invalid/yanShip.png",
            "name": "炎",
            "activeCount": 3,
        },
        {
            "bondId": "soloShip",
            "iconUrl": "https://example.invalid/soloShip.png",
            "name": "独行",
            "activeCount": 0,
        },
    ],
    "chars": [
        {
            "charId": "char_1039_thorn2",
            "avatarUrl": "https://example.invalid/char_1039_thorn2.png",
            "halfBodyUrl": "https://example.invalid/half_1039_thorn2.png",
            "name": "引星棘刺",
            "skills": [],
            "modules": [],
        }
    ],
    "items": [
        {
            "itemId": "chess_item_2_10_e_a",
            "iconUrl": "https://example.invalid/chess_item_2_10_e_a.png",
            "name": "灵巧涡轮手套",
        }
    ],
}

RECORD = {
    "id": "6379755-act3autochess-1794154580",
    "completeState": 0,
    "trophyBefore": 15,
    "trophyAfter": 16,
    "coinCost": 74,
    "syncCnt": 4,
    "killCnt": 104,
    "bandId": "band_weakness",
    "title": "",
    "bondInfo": [
        {"bondId": "soloShip", "layer": 0, "activate": 0},
        {"bondId": "yanShip", "layer": 4, "activate": 1},
    ],
    "chessSquad": [
        {
            "chessId": "chess_char_6_01_a",
            "equips": [{"equipId": "chess_item_2_10_e_a"}],
            "chessInfo": {
                "id": "chess_char_6_01_a",
                "charId": "char_1039_thorn2",
                "charName": "引星棘刺",
                "chessLevel": 6,
                "upgradeNum": 3,
            },
            "moduleId": "uniequip_002_thorn2",
            "skillId": "skchr_thorn2_2",
            "charId": "char_1039_thorn2",
        }
    ],
    "passRound": 7,
    "gameStartTs": "1794154580",
    "gameEndTs": "1794156731",
    "modeType": "MULTI",
    "modeDifficulty": "HARD",
    "versionId": "V3_1",
    "activityId": "act3autochess",
}

PLAYER_INFO = {
    "status": {
        "uid": "6379755",
        "name": "Coe#7127",
        "level": 120,
        "avatar": {"url": "https://example.invalid/avatar.png"},
        "secretary": {"charId": "char_002_amiya", "skinId": "char_1001_amiya2#1"},
    }
}


def test_roman_level():
    assert roman_level(1) == "I"
    assert roman_level(4) == "IV"
    assert roman_level(6) == "VI"
    assert roman_level(0) == "0"
    assert roman_level(None) == "0"
    assert roman_level("3") == "III"
    # Out-of-range levels clamp instead of crashing.
    assert roman_level(9) == "VIII"


def test_mode_labels():
    assert mode_label("MULTI") == "联合模拟"
    assert mode_label("SINGLE") == "独立模拟"
    assert mode_label("LOCAL") == "本地模拟"
    assert mode_label("") == "-"
    assert mode_label("UNKNOWN") == "UNKNOWN"


def test_difficulty_labels():
    assert difficulty_label("FUNNY") == "标准模拟"
    assert difficulty_label("NORMAL") == "险境模拟"
    assert difficulty_label("HARD") == "绝境模拟"
    assert difficulty_label("ABYSS") == "终极模拟"
    assert difficulty_label("") == "-"


def test_build_maps_indexes_by_id():
    maps = build_maps(RESOURCE)
    assert maps["bands"]["band_weakness"]["name"] == "以己之长"
    assert maps["bonds"]["yanShip"]["name"] == "炎"
    assert maps["chars"]["char_1039_thorn2"]["name"] == "引星棘刺"
    assert maps["items"]["chess_item_2_10_e_a"]["name"] == "灵巧涡轮手套"


def test_prepare_record_maps_fields():
    record = prepare_record(RECORD, build_maps(RESOURCE))
    assert record["success"] is False
    assert record["title"] == "模拟失败"
    assert record["pass_round"] == 7
    assert record["mode"] == "联合模拟"
    assert record["difficulty"] == "绝境模拟"
    assert record["strategy_name"] == "以己之长"
    assert record["band_icon"].endswith("band_weakness.png")
    assert record["trophy_before"] == 15
    assert record["trophy_after"] == 16
    assert record["kill_cnt"] == 104
    assert record["coin_cost"] == 74
    # syncCnt is intentionally not surfaced on the card.
    assert "sync_cnt" not in record
    # Chess cells carry only the portrait, Roman level and equip icons.
    unit = record["squad"][0]
    assert unit["roman"] == "VI"
    assert unit["avatar"].endswith("char_1039_thorn2.png")
    assert [e["icon"] for e in unit["equips"]] == [
        "https://example.invalid/chess_item_2_10_e_a.png"
    ]
    # Activated bonds sort first, then by descending layer.
    assert [b["name"] for b in record["bonds"]] == ["炎", "独行"]
    assert record["bonds"][0]["layer"] == 4
    assert record["bonds"][0]["activate"] is True


def test_prepare_record_ignores_record_title():
    # The badge always spells out the outcome, even when the payload carries a
    # ``title``; the raw field is empty in practice and must not win.
    success = prepare_record(
        {**RECORD, "title": "自定义", "completeState": 1}, build_maps(RESOURCE)
    )
    assert success["success"] is True
    assert success["title"] == "模拟成功"

    failure = prepare_record(
        {**RECORD, "title": "自定义", "completeState": 0}, build_maps(RESOURCE)
    )
    assert failure["success"] is False
    assert failure["title"] == "模拟失败"


def test_pick_char_tolerates_non_numeric_level():
    # A malformed ``chessLevel`` degrades to level 0 instead of raising outside
    # the command's try/except.
    unit = pick_char(
        build_maps(RESOURCE),
        {"chessInfo": {"charId": "char_1039_thorn2", "chessLevel": "unknown"}},
    )
    assert unit["level"] == 0
    assert unit["roman"] == "0"


def test_format_ts_invalid_yields_dash():
    assert format_ts(None) == "-"
    assert format_ts("not-a-number") == "-"


def test_build_user_falls_back_to_char_names():
    user = build_user(PLAYER_INFO, build_maps(RESOURCE), {"char_002_amiya": "阿米娅"})
    assert user["uid"] == "6379755"
    assert user["name"] == "Coe#7127"
    assert user["level"] == 120
    assert user["avatar"].endswith("avatar.png")
    # Amiya is absent from the guide resource, so the plugin's own table wins.
    assert user["secretary_name"] == "阿米娅"
    assert user["secretary_icon"] == ""


def test_build_user_without_secretary_is_empty():
    user = build_user({"status": {"uid": "1"}}, build_maps(RESOURCE), {})
    assert user["secretary_name"] == ""
    assert user["avatar"] == ""


def test_build_context_limits_and_builds_header():
    records = [RECORD] * 5
    context = build_context(
        RESOURCE, records, PLAYER_INFO, {"char_002_amiya": "阿米娅"}
    )
    assert len(context["records"]) == 3
    assert context["season_name"] == "规程"
    assert context["version"] == "V3_1"
    assert context["phase_name"] == "序列I"
    assert context["user"]["secretary_name"] == "阿米娅"


def test_build_context_handles_empty_records():
    context = build_context(RESOURCE, [], PLAYER_INFO, {})
    assert context["records"] == []
    assert context["version"] == "V3_1"


class _FakeSkland:
    """SklandClient stand-in returning fixed garrison payloads."""

    def __init__(self):
        self.called_with: tuple[str, str] | None = None

    async def get_garrison_resource(self, cred):
        return RESOURCE

    async def get_garrison_history_log(self, cred, uid, season_id):
        self.called_with = (uid, season_id)
        return [RECORD]


@pytest.mark.anyio
async def test_garrison_client_derives_season_id():
    skland = _FakeSkland()
    client = GarrisonClient(skland)
    resource, records = await client.fetch(Credential("t", "c"), "6379755")
    assert skland.called_with == ("6379755", "act3autochess")
    assert records == [RECORD]
    assert resource is RESOURCE


@pytest.mark.parametrize(
    ("text", "default", "expected"),
    [
        ("ark卫戍战绩", 3, 3),
        ("ark卫戍战绩 5", 3, 5),
        ("ark卫戍战绩 abc", 3, 3),
        ("ark卫戍战绩 0", 3, 0),
        ("ark卫戍列表", 15, 15),
        ("/ark卫戍列表 -2 9", 15, -2),
        ("ark卫戍列表 abc 7 12", 15, 7),
        ("ark卫戍列表 1.5", 15, 15),
        ("ark卫戍列表 5abc", 15, 15),
    ],
)
def test_parse_count(text, default, expected):
    assert parse_count(text, default) == expected


def test_format_short_ts_valid_and_invalid():
    value = datetime(2026, 11, 12, 9, 8).timestamp()
    assert format_short_ts(value) == "11-12 09:08"
    for invalid in (None, "abc", "", 10**30):
        assert format_short_ts(invalid) == "-"


def test_build_list_context_full_summary_and_ordered_rows():
    squad = [
        {"chessInfo": {"charName": name, "chessLevel": level}}
        for name, level in [("阿米娅", 1), ("引星棘刺", 6), ("陈", 4), ("能天使", 5)]
    ]
    records = [
        {**RECORD, "completeState": int(i % 2 == 0), "chessSquad": squad}
        for i in range(51)
    ]
    context = build_list_context(RESOURCE, records, PLAYER_INFO, {})
    assert context["summary"] == {
        "total": 51,
        "shown": 15,
        "cleared": 26,
        "cleared_percent": "51.0",
    }
    assert len(context["rows"]) == 15
    assert context["rows"][0] == {
        "start": format_short_ts(RECORD["gameStartTs"]),
        "difficulty": "绝境",
        "mode": "联合",
        "success": True,
        "trophy": "15→16",
        "rounds": 7,
        "core_ops": "引星棘刺、能天使、陈",
    }
    assert context["rows"][1]["success"] is False
    assert context["rows"][1]["trophy"] == "-"
    assert context["user"] == build_user(PLAYER_INFO, build_maps(RESOURCE), {})
    assert (context["season_name"], context["version"], context["phase_name"]) == (
        "规程",
        "V3_1",
        "序列I",
    )


def test_build_list_context_empty_and_short_squads():
    empty = build_list_context(None, [], None, {})
    assert empty["rows"] == []
    assert empty["summary"] == {
        "total": 0,
        "shown": 0,
        "cleared": 0,
        "cleared_percent": "0.0",
    }
    context = build_list_context(
        {}, [RECORD, {**RECORD, "chessSquad": []}], PLAYER_INFO, {}, limit=30
    )
    assert context["summary"]["shown"] == 2
    assert context["rows"][0]["core_ops"] == "引星棘刺"
    assert context["rows"][1]["core_ops"] == "-"
    assert context["version"] == "V3_1"


@pytest.fixture
def garrison_handlers():
    """Load real handlers without starting AstrBot or accessing account data."""
    source = ast.parse((Path(__file__).parents[1] / "main.py").read_text("utf-8"))
    names = {
        "show_garrison",
        "show_garrison_list",
        "show_garrison_trophy",
        "_garrison_text",
        "_garrison_list_text",
    }
    nodes = [
        node
        for node in ast.walk(source)
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef))
        and node.name in names
    ]
    for node in nodes:
        node.decorator_list = []
    client = SimpleNamespace(fetch=AsyncMock(return_value=(RESOURCE, [RECORD] * 51)))
    namespace = {
        "AstrMessageEvent": object,
        "Any": object,
        "parse_count": parse_count,
        "build_context": build_context,
        "build_list_context": build_list_context,
        "GarrisonClient": lambda skland: client,
        "GarrisonError": GarrisonError,
        "SklandError": SklandError,
        "NO_BINDING_TEXT": "请先绑定账号",
        "Image": SimpleNamespace(fromFileSystem=lambda path: path),
    }
    exec(
        compile(
            ast.fix_missing_locations(ast.Module(body=nodes, type_ignores=[])),
            "main.py",
            "exec",
        ),
        namespace,
    )
    plugin = SimpleNamespace(
        _resolve_binding=AsyncMock(return_value=({}, {"uid": "fixture"})),
        skland=SimpleNamespace(
            get_authorization=AsyncMock(return_value="fake"),
            get_credential=AsyncMock(return_value=Credential("t", "c")),
        ),
        _player_data=AsyncMock(return_value=PLAYER_INFO),
        _gamedata=SimpleNamespace(ensure=AsyncMock(), char_names={}),
        _report_query_error=AsyncMock(return_value="查询失败"),
        _render=AsyncMock(return_value=None),
        _garrison_text=namespace["_garrison_text"],
        _garrison_list_text=namespace["_garrison_list_text"],
    )
    return namespace, plugin, client


@pytest.mark.anyio
@pytest.mark.parametrize(
    ("handler", "command", "count", "expected"),
    [
        ("show_garrison", "ark卫戍战绩", "", 3),
        ("show_garrison", "ark卫戍战绩", "abc", 3),
        ("show_garrison", "ark卫戍战绩", "0", 1),
        ("show_garrison", "ark卫戍战绩", "99", 6),
        ("show_garrison", "ark卫戍战绩", "5", 5),
        ("show_garrison_list", "ark卫戍列表", "", 15),
        ("show_garrison_list", "ark卫戍列表", "abc", 15),
        ("show_garrison_list", "ark卫戍列表", "0", 1),
        ("show_garrison_list", "ark卫戍列表", "99", 30),
        ("show_garrison_list", "ark卫戍列表", "-2", 1),
    ],
)
async def test_handler_count_boundaries(
    garrison_handlers, handler, command, count, expected
):
    namespace, plugin, _ = garrison_handlers
    event = SimpleNamespace(
        message_str=f"{command} {count}", plain_result=lambda text: text
    )
    replies = [reply async for reply in namespace[handler](plugin, event)]
    assert len(replies) == 1
    template, payload = plugin._render.await_args.args
    is_list = handler == "show_garrison_list"
    assert template == ("garrison_list.html" if is_list else "garrison_recent.html")
    assert len(payload["garrison"]["rows" if is_list else "records"]) == expected


@pytest.mark.anyio
@pytest.mark.parametrize("handler", ["show_garrison", "show_garrison_list"])
@pytest.mark.parametrize("state", ["unbound", "error", "empty", "image"])
async def test_handler_outcomes(garrison_handlers, handler, state):
    namespace, plugin, client = garrison_handlers
    event = SimpleNamespace(
        message_str="ark卫戍列表",
        plain_result=lambda text: text,
        chain_result=lambda chain: chain,
    )
    if state == "unbound":
        plugin._resolve_binding.return_value = None
    elif state == "error":
        client.fetch.side_effect = GarrisonError("fixture error")
    elif state == "empty":
        client.fetch.return_value = RESOURCE, []
    else:
        plugin._render.return_value = Path("fixture.png")
    replies = [reply async for reply in namespace[handler](plugin, event)]
    assert replies == [
        {
            "unbound": "请先绑定账号",
            "error": "查询失败",
            "empty": "没有查询到卫戍协议战绩。",
            "image": ["fixture.png"],
        }[state]
    ]
    if state != "image":
        plugin._render.assert_not_awaited()
    if state == "unbound":
        client.fetch.assert_not_awaited()


def test_garrison_list_text_bounds(garrison_handlers):
    namespace, _, _ = garrison_handlers
    context = build_list_context(RESOURCE, [RECORD] * 51, PLAYER_INFO, {}, limit=30)
    text = namespace["_garrison_list_text"](context)
    assert len(text.splitlines()) == 13
    assert text.splitlines()[2] == (
        f"{format_short_ts(RECORD['gameStartTs'])} 绝境/联合 失败 - 7 [引星棘刺]"
    )
    assert text.endswith("……共 51 场，这里只列前 10 场")
    context = build_list_context(RESOURCE, [RECORD], PLAYER_INFO, {})
    assert "只列前 10" not in namespace["_garrison_list_text"](context)


def test_garrison_list_template_smoke():
    env = Environment(
        loader=DictLoader({**TEMPLATES, "_macros.html": MACROS}),
        autoescape=True,
        undefined=StrictUndefined,
    )
    context = build_list_context(RESOURCE, [RECORD] * 51, PLAYER_INFO, {})
    html = env.get_template("garrison_list.html").render(
        base_css=BASE_CSS, garrison=context
    )
    assert "卫戍战绩列表" in html
    assert "规程 · V3_1" in html
    assert "共 51 场 · 显示最近 15 场 · 通关 0 场（0.0%）" in html
    assert html.count('class="g-lose"') == 15


@pytest.mark.anyio
async def test_role_trophy_rank_and_cache(tmp_path):
    skland = SimpleNamespace(get_authorization=AsyncMock(), get_credential=AsyncMock())
    path = tmp_path / "garrison_trophy_cache.json"
    ranking = GarrisonTrophyRanking(path, skland)
    active = peak = 0

    async def fetch(cred, uid):
        nonlocal active, peak
        active += 1
        peak = max(active, peak)
        await asyncio.sleep(0)
        active -= 1
        if uid == "bad":
            raise GarrisonError("offline")
        if uid == "empty":
            return {}, []
        return {}, [
            {"trophyAfter": 12 if uid != "three" else 8, "completeState": 0},
            {"trophyAfter": 0, "completeState": 1},
        ]

    ranking.client.fetch = AsyncMock(side_effect=fetch)
    roles = {
        uid: (f"Role {uid}", "token") for uid in ("one", "two", "three", "bad", "empty")
    }
    result = await ranking.rank(roles, {"two"})
    assert peak == 4
    assert [row["rank"] for row in result["rows"]] == [1, 1, 3]
    assert [row["trophy"] for row in result["rows"]] == [12, 12, 8]
    assert result["rows"][1]["own"] and result["rows"][1]["games"] == 2
    assert result["failed"] == result["empty"] == 1
    assert "token" not in path.read_text(encoding="utf-8")
    reopened = GarrisonTrophyRanking(path, skland)
    reopened.client.fetch = AsyncMock()
    await reopened.rank({uid: roles[uid] for uid in ("one", "two", "three")}, set())
    reopened.client.fetch.assert_not_awaited()
    assert skland.get_authorization.await_count == 5


@pytest.mark.anyio
async def test_role_trophy_group_scope_and_empty(garrison_handlers):
    namespace, plugin, _ = garrison_handlers

    def binding(uid: str) -> dict[str, str]:
        return {"uid": uid, "nick_name": "Role " + uid}

    plugin.store = SimpleNamespace(
        all_users=AsyncMock(
            return_value={
                "10": {
                    "token": "member",
                    "primary_uid": "main",
                    "bindings": [binding("alt"), binding("main")],
                },
                "20": {
                    "token": "outsider",
                    "primary_uid": "other",
                    "bindings": [binding("other")],
                },
            }
        )
    )
    plugin._garrison_trophies = SimpleNamespace(
        rank=AsyncMock(
            return_value={
                "entries": 1,
                "updated": "2026-11-19 12:00",
                "failed": 0,
                "empty": 0,
                "rows": [
                    {
                        "uid": "main",
                        "name": "Role main",
                        "rank": 1,
                        "trophy": 12,
                        "games": 2,
                        "own": True,
                    }
                ],
            }
        )
    )
    plugin._render = AsyncMock(return_value=None)
    action = AsyncMock(return_value=[{"user_id": 30}])
    event = SimpleNamespace(
        message_str="ark卫戍排行",
        get_group_id=lambda: "123",
        get_sender_id=lambda: "10",
        bot=SimpleNamespace(call_action=action),
        plain_result=str,
    )
    handler = namespace["show_garrison_trophy"]
    assert "还没有成员绑定" in [item async for item in handler(plugin, event)][0]
    plugin._garrison_trophies.rank.assert_not_awaited()
    action.return_value = [{"user_id": 10}]
    messages = [item async for item in handler(plugin, event)]
    action.assert_awaited_with("get_group_member_list", group_id=123)
    plugin._garrison_trophies.rank.assert_awaited_once_with(
        {"main": ("Role main", "member")}, {"main"}, force=False
    )
    assert "Role main（你）" in messages[-1]
    template, payload = plugin._render.await_args.args
    env = Environment(
        loader=DictLoader({**TEMPLATES, "_macros.html": MACROS}),
        undefined=StrictUndefined,
    )
    rendered = env.get_template(template).render(base_css="", **payload)
    assert 'class="t-own"' in rendered and "uid main · 2 场记录" in rendered
