import itertools
from typing import Any


def generate_dict_cartesian_product(
    parameters: dict[str, Any],
) -> list[dict[str, Any]]:
    """
    Build cartesian combinations from dict values.

    Scalar values are treated as single-option lists.
    """
    keys: list[str] = []
    values: list[list[Any]] = []

    for key, value in parameters.items():
        keys.append(key)
        if isinstance(value, list):
            values.append(value)
        else:
            values.append([value])

    all_combinations = itertools.product(*values)
    return [dict(zip(keys, combo)) for combo in all_combinations]
