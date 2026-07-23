"""In-memory state manager for Recall app."""

import uuid
from dataclasses import dataclass
from datetime import datetime, timedelta
from enum import Enum
from typing import Dict, List, Optional


class CardRating(str, Enum):
    """SM-2 rating options."""

    AGAIN = "again"
    HARD = "hard"
    GOOD = "good"
    EASY = "easy"


@dataclass
class Card:
    """Flashcard data structure."""

    id: str
    deck: str
    front: str
    back: str
    ease: float  # ease factor
    interval: int  # interval in days
    due_at: datetime
    created_at: datetime
    reviews: int = 0
    last_reviewed_at: Optional[datetime] = None


class State:
    """In-memory state manager."""

    def __init__(self):
        self.cards: Dict[str, Card] = {}
        self.reviews: List[Dict] = []

    def add_card(self, front: str, back: str, deck: str = "default") -> str:
        """Add a new card with immediate due date."""
        card_id = str(uuid.uuid4())

        # Initial SM-2 values
        card = Card(
            id=card_id,
            deck=deck,
            front=front,
            back=back,
            ease=2.5,  # default ease factor
            interval=1,  # 1 day for first review
            due_at=datetime.now(),
            created_at=datetime.now(),
            reviews=0,
        )

        self.cards[card_id] = card
        return card_id

    def get_next_due_card(self, deck: Optional[str] = None) -> Optional[Card]:
        """Get the next due card for review."""
        now = datetime.now()
        due_cards = []

        for card in self.cards.values():
            if deck is None or card.deck == deck:
                if card.due_at <= now:
                    due_cards.append(card)

        if not due_cards:
            return None

        # Return the earliest due card
        return min(due_cards, key=lambda c: c.due_at)

    def due_count(self, deck: Optional[str] = None) -> int:
        """Count cards currently due, optionally filtered by deck."""
        now = datetime.now()
        return sum(
            1
            for card in self.cards.values()
            if (deck is None or card.deck == deck) and card.due_at <= now
        )

    def grade_card(self, card_id: str, rating: CardRating) -> bool:
        """Apply SM-2 algorithm to grade a card and reschedule."""
        if card_id not in self.cards:
            return False

        card = self.cards[card_id]
        now = datetime.now()

        # Record review
        self.reviews.append({"card_id": card_id, "rating": rating, "reviewed_at": now})

        # Update card review stats
        card.last_reviewed_at = now
        card.reviews += 1

        # SM-2 algorithm
        if rating == CardRating.AGAIN:
            card.interval = 1  # reset to 1 day
            card.ease = max(1.3, card.ease - 0.2)  # decrease ease factor
        else:
            # Calculate new interval
            if card.reviews == 1:
                # First review after initial learning
                if rating == CardRating.GOOD:
                    card.interval = 1
                elif rating == CardRating.EASY:
                    card.interval = 4
                elif rating == CardRating.HARD:
                    card.interval = 1
            else:
                # Subsequent reviews
                if rating == CardRating.HARD:
                    card.interval = max(1, int(card.interval * 1.2))
                elif rating == CardRating.GOOD:
                    card.interval = int(card.interval * card.ease)
                elif rating == CardRating.EASY:
                    card.interval = int(card.interval * card.ease * 1.3)

            # Update ease factor
            if rating == CardRating.HARD:
                card.ease = max(1.3, card.ease - 0.15)
            elif rating == CardRating.GOOD:
                card.ease = max(1.3, card.ease)  # no change for good
            elif rating == CardRating.EASY:
                card.ease = card.ease + 0.15

        # Cap ease factor
        card.ease = max(1.3, min(card.ease, 2.5))

        # Set new due date
        card.due_at = now + timedelta(days=card.interval)

        return True

    def get_stats(self, deck: Optional[str] = None) -> Dict:
        """Get deck statistics."""
        now = datetime.now()
        today_start = datetime(now.year, now.month, now.day)
        today_end = today_start + timedelta(days=1)

        total_cards = 0
        due_today = 0
        reviewed_today = 0
        total_reviews = 0

        for card in self.cards.values():
            if deck is None or card.deck == deck:
                total_cards += 1
                if card.due_at <= now:
                    due_today += 1
                if card.last_reviewed_at and today_start <= card.last_reviewed_at < today_end:
                    reviewed_today += 1
                total_reviews += card.reviews

        # Calculate streak (days with at least one review)
        streak = 0
        if self.reviews:
            # Get unique days with reviews
            review_days = set()
            for review in self.reviews:
                if deck is None or review["card_id"] in [
                    c.id for c in self.cards.values() if c.deck == deck
                ]:
                    review_date = review["reviewed_at"].date()
                    review_days.add(review_date)

            # Sort and check consecutive days from today backward
            sorted_days = sorted(review_days, reverse=True)
            current_date = now.date()
            streak = 0

            for i, review_date in enumerate(sorted_days):
                if review_date == current_date - timedelta(days=i):
                    streak += 1
                else:
                    break

        return {
            "total_cards": total_cards,
            "due_today": due_today,
            "reviewed_today": reviewed_today,
            "total_reviews": total_reviews,
            "streak": streak,
        }


# Global state instance
state = State()
