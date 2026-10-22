from core.cards import build_note_context
from core.operators import group_operators, training_summary


def test_training_summary_counts_only_unlocked_unique_real_modules():
    char = {
        "skills": [
            {"id": "s1", "specializeLevel": 0},
            {"id": "s2", "specializeLevel": 3},
        ],
        "equip": [
            {"id": "uniequip_001_a", "level": 1},
            {"id": "x", "level": 0},
            {"id": "y", "level": 1},
            {"id": "y", "level": 3},
        ],
    }
    result = training_summary(char, {"y": {"name": "测试模组"}})
    assert result["mastery_text"] == "S1 专0 / S2 专3"
    assert result["module_text"] == "测试模组 Lv.3"
    assert len(result["unlocked_modules"]) == 1


def test_note_matches_owned_training_and_counts_all_modules():
    chars = [
        {
            "charId": "a",
            "skills": [{"id": "s", "specializeLevel": 2}],
            "equip": [{"id": "x", "level": 1}, {"id": "y", "level": 3}],
        },
        {"charId": "b", "equip": [{"id": "z", "level": 0}]},
    ]
    data = {
        "chars": chars,
        "charInfoMap": {"a": {"name": "甲", "profession": "MEDIC"}},
        "equipmentInfoMap": {"x": {"name": "甲模组"}},
        "status": {"secretary": {"charId": "a"}},
        "assistChars": [{"charId": "a"}],
    }
    note = build_note_context(data, now=0)
    assert note["module_count"] == 2
    assert note["module_stage3_count"] == 1
    assert note["module_operator_count"] == 1
    assert note["secretary"]["mastery_text"] == "S1 专2"
    assert note["assist"][0]["module_text"].startswith("甲模组 Lv.1")
    groups = group_operators(chars, data["charInfoMap"], data["equipmentInfoMap"])
    assert groups[0]["operators"][0]["module_text"].startswith("甲模组 Lv.1")


def test_missing_training_is_safe():
    assert training_summary({})["mastery_text"] == "暂无技能数据"
    note = build_note_context({}, now=0)
    assert note["module_count"] == 0
    assert note["module_stage3_count"] == 0
    assert note["module_operator_count"] == 0


def test_potential_uses_player_facing_levels():
    assert training_summary({"potentialRank": 0})["potential_level"] == 1
    assert training_summary({"potentialRank": 5})["potential_level"] == 6
    assert training_summary({})["potential_level"] is None


def test_original_metadata_and_locked_modules_are_excluded_everywhere():
    from core.operators import build_operator_context

    equips = [
        {"id": "legacy_base", "level": 1, "locked": False},
        {"id": "locked_real", "level": 3, "locked": True},
        {"id": "real", "level": 3, "locked": False},
    ]
    metadata = {
        "legacy_base": {"name": "基础证章", "typeIcon": "original"},
        "locked_real": {"typeIcon": "swo-x"},
        "real": {"typeIcon": "swo-y"},
    }
    char = {"charId": "a", "equip": equips}
    assert [
        item["id"] for item in training_summary(char, metadata)["unlocked_modules"]
    ] == ["real"]
    detail = build_operator_context({"char_id": "a", "equip": equips}, metadata)
    assert [item["id"] for item in detail["equips"]] == ["real"]
    note = build_note_context({"chars": [char], "equipmentInfoMap": metadata}, now=0)
    assert (
        note["module_count"],
        note["module_stage3_count"],
        note["module_operator_count"],
    ) == (1, 1, 1)


def test_elite_and_mastery_totals_count_operators_and_unique_skills():
    data = {
        "chars": [
            {
                "charId": "a",
                "evolvePhase": 2,
                "skills": [
                    {"id": "s1", "specializeLevel": 3},
                    {"id": "s2", "specializeLevel": 3},
                    {"id": "s2", "specializeLevel": 3},
                ],
            },
            {
                "charId": "b",
                "evolvePhase": 1,
                "skills": [{"id": "s3", "specializeLevel": 2}],
            },
            {"charId": "c", "evolvePhase": 2, "skills": None},
        ]
    }
    note = build_note_context(data, now=0)
    assert note["elite2_count"] == 2
    assert note["mastery3_count"] == 2
    empty = build_note_context({}, now=0)
    assert empty["elite2_count"] == empty["mastery3_count"] == 0
