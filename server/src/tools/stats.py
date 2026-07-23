"""Statistics tool module."""

from typing import Optional

from state import state


def stats(deck: Optional[str] = None) -> dict:
    """
    Get deck statistics: cards total, due today, reviewed today, streak.

    Args:
        deck: Optional deck name to filter by

    Returns:
        Dictionary with deck statistics
    """
    return state.get_stats(deck)
