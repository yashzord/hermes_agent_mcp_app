"""Pure SM-2 scheduling - the math only, no storage or I/O.

Kept separate so the scheduling rules stay boring, correct, and testable
without a database. See PROJECT.md §3.
"""

from enum import Enum

DEFAULT_EASE = 2.5
MIN_EASE = 1.3
MAX_EASE = 2.5  # ponytail: capped; textbook SM-2 lets ease grow past 2.5.
# Uncap here if `easy` should accelerate cards.


class CardRating(str, Enum):
    """SM-2 rating options."""

    AGAIN = "again"
    HARD = "hard"
    GOOD = "good"
    EASY = "easy"


def schedule(
    ease: float, interval: int, review_number: int, rating: CardRating
) -> tuple[float, int]:
    """Return (new_ease, new_interval_days) for a graded card.

    Args:
        ease: current ease factor
        interval: current interval in days
        review_number: 1-based index of THIS review (1 = first time graded)
        rating: the grade just given

    The interval/ease transitions are the classic Anki-style simplification.
    """
    if rating == CardRating.AGAIN:
        interval = 1
        ease = ease - 0.2
    else:
        if review_number <= 1:
            interval = {CardRating.GOOD: 1, CardRating.EASY: 4, CardRating.HARD: 1}[rating]
        elif rating == CardRating.HARD:
            interval = max(1, int(interval * 1.2))
        elif rating == CardRating.GOOD:
            interval = int(interval * ease)
        elif rating == CardRating.EASY:
            interval = int(interval * ease * 1.3)

        if rating == CardRating.HARD:
            ease = ease - 0.15
        elif rating == CardRating.EASY:
            ease = ease + 0.15

    ease = max(MIN_EASE, min(ease, MAX_EASE))
    return ease, max(1, interval)


def _demo() -> None:
    """Runnable self-check: SM-2 invariants hold."""
    # ease never drops below the floor, even after many 'again's
    ease, interval = DEFAULT_EASE, 1
    for _ in range(10):
        ease, interval = schedule(ease, interval, 1, CardRating.AGAIN)
    assert ease == MIN_EASE, ease
    assert interval == 1

    # 'again' resets interval to 1 mid-sequence
    ease, interval = schedule(DEFAULT_EASE, 10, 3, CardRating.AGAIN)
    assert interval == 1

    # repeated 'good' grows the interval
    ease, interval = DEFAULT_EASE, 1
    seen = []
    for n in range(1, 5):
        ease, interval = schedule(ease, interval, n, CardRating.GOOD)
        seen.append(interval)
    assert seen == sorted(seen) and seen[-1] > 1, seen
    print("sm2 self-check OK:", seen)


if __name__ == "__main__":
    _demo()
