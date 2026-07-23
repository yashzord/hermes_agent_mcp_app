"""Add card tool module."""

from state import state


def add_card(front: str, back: str, deck: str = "default") -> str:
    """
    Add a new flashcard, scheduled immediately due.

    Args:
        front: Text on the front of the card
        back: Text on the back of the card
        deck: Optional deck name (default: "default")

    Returns:
        Card ID of the newly created card
    """
    card_id = state.add_card(front, back, deck)
    return f"Card added with ID: {card_id}"
