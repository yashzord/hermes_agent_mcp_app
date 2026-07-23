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
    due = state.grade_card(card_id, rating)

    if due is None:
        return f"Card with ID {card_id} not found."

    return f"Card graded as '{CardRating(rating).value}'. Next review: {due:%Y-%m-%d %H:%M}."
