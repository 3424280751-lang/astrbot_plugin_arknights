from core.assets import owned_secretary_artworks
from core.cards import build_note_context


def test_only_owned_matching_skins_and_unlocked_promotion_are_candidates():
    skins = [
        {"id": "char_a@summer#1"},
        {"id": "char_a@summer#1"},
        {"id": "char_b@summer#1"},
    ]
    meta = {
        "char_a@summer#1": {"charId": "char_a", "name": "夏日"},
        "char_a@winter#1": {"charId": "char_a", "name": "未拥有"},
    }
    pool = owned_secretary_artworks("char_a", 1, skins, meta)
    assert [item["id"] for item in pool] == ["char_a#1", "char_a@summer#1"]
    assert len(owned_secretary_artworks("char_a", 2, skins, meta)) == 3
    assert owned_secretary_artworks("", 2, skins) == []


def test_note_random_keeps_current_secretary_and_uses_owned_pool(monkeypatch):
    monkeypatch.setattr("core.cards.random.choice", lambda values: values[-1])
    note = build_note_context(
        {
            "status": {"secretary": {"charId": "char_a"}},
            "chars": [{"charId": "char_a", "evolvePhase": 2}],
            "skins": [{"id": "char_a@summer#1"}],
            "skinInfoMap": {"char_a@summer#1": {"charId": "char_a", "name": "夏日"}},
        },
        secretary_mode="random",
    )
    assert note["secretary"]["char_id"] == "char_a"
    assert note["secretary"]["artwork_name"] == "夏日"
    assert note["secretary"]["artwork_pool_size"] == 3
    assert "summer" in note["secretary"]["portrait"]
