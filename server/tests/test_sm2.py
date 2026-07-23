"""Pure SM-2 scheduling checks (no storage). Run: uv run pytest (from server/)."""

from sm2 import DEFAULT_EASE, MIN_EASE, CardRating, schedule


def test_ease_floor_holds_under_repeated_again():
    ease, interval = DEFAULT_EASE, 1
    for _ in range(10):
        ease, interval = schedule(ease, interval, 1, CardRating.AGAIN)
    assert ease == MIN_EASE
    assert interval == 1


def test_again_resets_interval_to_one():
    _, interval = schedule(DEFAULT_EASE, 20, 5, CardRating.AGAIN)
    assert interval == 1


def test_good_grows_interval():
    ease, interval = DEFAULT_EASE, 1
    seen = []
    for n in range(1, 5):
        ease, interval = schedule(ease, interval, n, CardRating.GOOD)
        seen.append(interval)
    assert seen == sorted(seen)
    assert seen[-1] > 1


def test_interval_never_below_one():
    _, interval = schedule(DEFAULT_EASE, 1, 2, CardRating.HARD)
    assert interval >= 1


def test_ease_capped_at_max():
    ease, _ = schedule(DEFAULT_EASE, 1, 3, CardRating.EASY)
    assert ease <= 2.5
