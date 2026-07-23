"""SQLite State integration checks against fresh temp databases."""

import os
import tempfile

from state import CardRating, State


def _fresh() -> State:
    fd, path = tempfile.mkstemp(suffix=".db")
    os.close(fd)
    os.remove(path)  # let State create + seed a clean DB
    return State(path)


def test_seed_deck_loads_on_empty_db():
    s = _fresh()
    assert s.get_stats()["total_cards"] >= 20


def test_add_and_review_next():
    s = _fresh()
    cid = s.add_card("q", "a", "deckX")
    card = s.get_next_due_card("deckX")
    assert card is not None and card.id == cid and card.front == "q"


def test_grade_reschedules_card_out_of_due():
    s = _fresh()
    cid = s.add_card("q", "a", "deckX")
    due = s.grade_card(cid, CardRating.GOOD)
    assert due is not None
    assert s.get_next_due_card("deckX") is None  # no longer due today


def test_grade_unknown_card_returns_none():
    s = _fresh()
    assert s.grade_card("nope", CardRating.GOOD) is None


def test_due_count_and_stats_scope_to_deck():
    s = _fresh()
    s.add_card("a", "1", "deckX")
    s.add_card("b", "2", "deckX")
    assert s.due_count("deckX") == 2
    st = s.get_stats("deckX")
    assert st["total_cards"] == 2 and st["due_today"] == 2


def test_streak_counts_today_after_a_review():
    s = _fresh()
    cid = s.add_card("q", "a", "deckX")
    s.grade_card(cid, CardRating.GOOD)
    assert s.get_stats()["streak"] == 1


def test_persistence_across_reopen():
    fd, path = tempfile.mkstemp(suffix=".db")
    os.close(fd)
    os.remove(path)
    s1 = State(path)
    cid = s1.add_card("keep", "me", "deckX")
    s2 = State(path)  # reopen same file
    assert s2.get_next_due_card("deckX").id == cid
