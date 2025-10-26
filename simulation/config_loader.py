import json
import itertools


def load_config(path: str) -> dict:
    """Load configuration from a JSON file."""
    with open(path, "r") as f:
        return json.load(f)


def generate_parameter_combinations(parameters: dict):
    """
    Generate all possible combinations of the parameters.
    Returns a list of dicts.
    """
    # Only consider parameters that are lists (expandable)
    keys = []
    values = []
    for k, v in parameters.items():
        if isinstance(v, list):
            keys.append(k)
            values.append(v)
        else:
            # Convert single values to list for consistency
            keys.append(k)
            values.append([v])
    
    # Cartesian product
    all_combinations = list(itertools.product(*values))
    
    # Convert each combination to a dict
    combinations_dicts = [dict(zip(keys, combo)) for combo in all_combinations]
    return combinations_dicts
