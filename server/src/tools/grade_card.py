"""Grade card tool module."""

from state import CardRating, state


def grade_card(card_id: str, rating: CardRating) -> str:
    """
    Grade a reviewed card and reschedule it with SM-2.

    Args:
        card_id: ID of the card to grade
        rating: Rating (again/hard/good/easy)

    Returns:
        Success or error message
    """
    success = state.grade_card(card_id, rating)

    if not success:
        return f"Card with ID {card_id} not found."

    card = state.cards[card_id]
    next_due = card.due_at.strftime("%Y-%m-%d %H:%M")
    return f"Card graded as '{rating.value}'. Next review scheduled for {next_due}."
