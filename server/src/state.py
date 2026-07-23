"""SQLite-backed state for Recall (PROJECT.md §4 data model).

Same interface the tools used with the in-memory version; storage is now a
SQLite file so a deployed server keeps decks across restarts.
"""

import os
import sqlite3
import uuid
from dataclasses import dataclass
from datetime import date, datetime, timedelta
from typing import Optional

from seed import SEED_CARDS, SEED_DECK
from sm2 import DEFAULT_EASE, CardRating, schedule

# Re-exported so `from state import CardRating` keeps working.
__all__ = ["State", "CardRating", "state"]

SCHEMA = """
CREATE TABLE IF NOT EXISTS cards (
    id TEXT PRIMARY KEY,
    deck TEXT NOT NULL,
    front TEXT NOT NULL,
    back TEXT NOT NULL,
    ease REAL NOT NULL,
    interval_days INTEGER NOT NULL,
    due_at TEXT NOT NULL,
    created_at TEXT NOT NULL,
    reviews INTEGER NOT NULL DEFAULT 0,
    last_reviewed_at TEXT
);
CREATE TABLE IF NOT EXISTS reviews (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    card_id TEXT NOT NULL,
    rating TEXT NOT NULL,
    reviewed_at TEXT NOT NULL
);
"""


@dataclass
class Card:
    """A flashcard row, hydrated for the tools that read .front/.back/etc."""

    id: str
    deck: str
    front: str
    back: str
    ease: float
    interval_days: int
    due_at: datetime
    created_at: datetime
    reviews: int


def _now() -> datetime:
    return datetime.now()


class State:
    """SQLite persistence with the same surface the tools call."""

    def __init__(self, db_path: Optional[str] = None):
        self.db_path = db_path or os.environ.get("RECALL_DB", "recall.db")
        with self._connect() as conn:
            conn.executescript(SCHEMA)
        self._seed_if_empty()

    def _connect(self) -> sqlite3.Connection:
        # ponytail: a fresh connection per operation. Fine for a single-container
        # personal app; add a pool if throughput ever matters.
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn

    def _seed_if_empty(self) -> None:
        with self._connect() as conn:
            (count,) = conn.execute("SELECT COUNT(*) FROM cards").fetchone()
            if count == 0:
                for front, back in SEED_CARDS:
                    self._insert(conn, front, back, SEED_DECK)

    def _insert(self, conn: sqlite3.Connection, front: str, back: str, deck: str) -> str:
        card_id = str(uuid.uuid4())
        now = _now().isoformat()
        conn.execute(
            "INSERT INTO cards "
            "(id, deck, front, back, ease, interval_days, due_at, created_at, reviews) "
            "VALUES (?, ?, ?, ?, ?, ?, ?, ?, 0)",
            (card_id, deck, front, back, DEFAULT_EASE, 1, now, now),
        )
        return card_id

    def add_card(self, front: str, back: str, deck: str = "default") -> str:
        """Insert a card, scheduled immediately due."""
        with self._connect() as conn:
            return self._insert(conn, front, back, deck)

    def _hydrate(self, row: sqlite3.Row) -> Card:
        return Card(
            id=row["id"],
            deck=row["deck"],
            front=row["front"],
            back=row["back"],
            ease=row["ease"],
            interval_days=row["interval_days"],
            due_at=datetime.fromisoformat(row["due_at"]),
            created_at=datetime.fromisoformat(row["created_at"]),
            reviews=row["reviews"],
        )

    def get_next_due_card(self, deck: Optional[str] = None) -> Optional[Card]:
        """Earliest due card, optionally within a deck."""
        now = _now().isoformat()
        clause = "" if deck is None else " AND deck = ?"
        params = (now,) if deck is None else (now, deck)
        with self._connect() as conn:
            row = conn.execute(
                f"SELECT * FROM cards WHERE due_at <= ?{clause} ORDER BY due_at LIMIT 1",
                params,
            ).fetchone()
        return self._hydrate(row) if row else None

    def due_count(self, deck: Optional[str] = None) -> int:
        """Count cards currently due, optionally within a deck."""
        now = _now().isoformat()
        clause = "" if deck is None else " AND deck = ?"
        params = (now,) if deck is None else (now, deck)
        with self._connect() as conn:
            (n,) = conn.execute(
                f"SELECT COUNT(*) FROM cards WHERE due_at <= ?{clause}", params
            ).fetchone()
        return n

    def grade_card(self, card_id: str, rating: CardRating) -> Optional[datetime]:
        """Apply SM-2, reschedule, log the review. Returns new due date or None."""
        rating = CardRating(rating)
        now = _now()
        with self._connect() as conn:
            row = conn.execute("SELECT * FROM cards WHERE id = ?", (card_id,)).fetchone()
            if row is None:
                return None
            reviews = row["reviews"] + 1
            ease, interval = schedule(row["ease"], row["interval_days"], reviews, rating)
            due = now + timedelta(days=interval)
            conn.execute(
                "UPDATE cards SET ease = ?, interval_days = ?, due_at = ?, "
                "reviews = ?, last_reviewed_at = ? WHERE id = ?",
                (ease, interval, due.isoformat(), reviews, now.isoformat(), card_id),
            )
            conn.execute(
                "INSERT INTO reviews (card_id, rating, reviewed_at) VALUES (?, ?, ?)",
                (card_id, rating.value, now.isoformat()),
            )
        return due

    def get_stats(self, deck: Optional[str] = None) -> dict:
        """Cards total / due today / reviewed today / total reviews / streak."""
        now = _now()
        now_iso = now.isoformat()
        today_start = datetime(now.year, now.month, now.day).isoformat()
        clause = "" if deck is None else " AND deck = ?"
        deck_params: tuple = () if deck is None else (deck,)
        with self._connect() as conn:
            (total,) = conn.execute(
                f"SELECT COUNT(*) FROM cards WHERE 1 = 1{clause}", deck_params
            ).fetchone()
            (due,) = conn.execute(
                f"SELECT COUNT(*) FROM cards WHERE due_at <= ?{clause}",
                (now_iso, *deck_params),
            ).fetchone()
            (reviewed,) = conn.execute(
                f"SELECT COUNT(*) FROM cards WHERE last_reviewed_at >= ?{clause}",
                (today_start, *deck_params),
            ).fetchone()
            (total_reviews,) = conn.execute(
                f"SELECT COALESCE(SUM(reviews), 0) FROM cards WHERE 1 = 1{clause}",
                deck_params,
            ).fetchone()
            # Streak is a global study habit, not per-deck.
            day_rows = conn.execute(
                "SELECT DISTINCT substr(reviewed_at, 1, 10) AS d FROM reviews ORDER BY d DESC"
            ).fetchall()

        streak = 0
        for i, r in enumerate(day_rows):
            if date.fromisoformat(r["d"]) == now.date() - timedelta(days=i):
                streak += 1
            else:
                break

        return {
            "total_cards": total,
            "due_today": due,
            "reviewed_today": reviewed,
            "total_reviews": total_reviews,
            "streak": streak,
        }


# Global instance the tools import.
state = State()
