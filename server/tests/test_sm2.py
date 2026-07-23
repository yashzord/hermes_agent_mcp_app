"""SM-2 scheduling and tool round-trip checks (Phase 2 acceptance).

Run: uv run pytest  (from server/)
"""

import sys
from datetime import datetime
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))

from state import CardRating, State  # noqa: E402


def _force_due(card):
    card.due_at = datetime.now()


def test_add_card_starts_due():
    s = State()
    cid = s.add_card("q", "a")
    assert s.get_next_due_card() is not None
    assert s.cards[cid].ease == 2.5


def test_again_resets_interval_to_one():
    s = State()
    cid = s.add_card("q", "a")
    c = s.cards[cid]
    s.grade_card(cid, CardRating.GOOD)
    _force_due(c)
    s.grade_card(cid, CardRating.GOOD)
    assert c.interval > 1
    _force_due(c)
    s.grade_card(cid, CardRating.AGAIN)
    assert c.interval == 1


def test_ease_floor_holds_under_repeated_again():
    s = State()
    cid = s.add_card("q", "a")
    c = s.cards[cid]
    for _ in range(10):
        _force_due(c)
        s.grade_card(cid, CardRating.AGAIN)
    assert c.ease >= 1.3


def test_intervals_grow_on_good():
    s = State()
    cid = s.add_card("q", "a")
    c = s.cards[cid]
    seen = []
    for _ in range(4):
        _force_due(c)
        s.grade_card(cid, CardRating.GOOD)
        seen.append(c.interval)
    # non-decreasing and eventually beyond the initial day
    assert seen == sorted(seen)
    assert seen[-1] > 1


def test_grade_unknown_card_returns_false():
    s = State()
    assert s.grade_card("nope", CardRating.GOOD) is False


def test_stats_and_due_count():
    s = State()
    s.add_card("a", "1", "deckA")
    s.add_card("b", "2", "deckA")
    s.add_card("c", "3", "deckB")
    st = s.get_stats("deckA")
    assert st["total_cards"] == 2
    assert st["due_today"] == 2
    assert s.due_count("deckA") == 2
    assert s.due_count() == 3
