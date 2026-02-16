from typing import Any


def resolve_positive_int(value: Any, default: int = 1) -> int:
    """
    Resolve an input value into a positive int.

    If `value` is a list, the first element is used.
    """
    candidate = value[0] if isinstance(value, list) and value else value
    try:
        parsed = int(candidate)
    except (TypeError, ValueError):
        parsed = default
    return max(parsed, 1)
