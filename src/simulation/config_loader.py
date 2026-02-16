from typing import Any

from src.utils.combinatorics import generate_dict_cartesian_product
from src.utils.json_io import load_json_file


def load_config(path: str) -> dict[str, Any]:
    """Load configuration from a JSON file."""
    return load_json_file(path)


def generate_parameter_combinations(parameters: dict[str, Any]) -> list[dict[str, Any]]:
    """
    Generate all possible combinations of the parameters.
    Returns a list of dicts.
    """
    return generate_dict_cartesian_product(parameters)
