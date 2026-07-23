"""Review next card tool module."""

from typing import Optional

from state import state


def review_next(deck: Optional[str] = None) -> dict:
    """
    Get the next due card for review.

    Args:
        deck: Optional deck name to filter by

    Returns:
        Dictionary with card details, plus due_count (how many cards are
        currently due in scope), or a message if nothing is due.
    """
    card = state.get_next_due_card(deck)

    if card is None:
        return {"message": "No cards due for review", "due": False, "due_count": 0}

    return {
        "card_id": card.id,
        "front": card.front,
        "back": card.back,
        "deck": card.deck,
        "due": True,
        "due_count": state.due_count(deck),
    }
