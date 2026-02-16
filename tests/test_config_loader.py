import json
import tempfile
import unittest

from src.simulation.config_loader import generate_parameter_combinations, load_config


class ConfigLoaderTests(unittest.TestCase):
    def test_load_config(self) -> None:
        payload = {"num_simulations": 1, "parameters": {"a": [1, 2], "b": 5}}
        with tempfile.NamedTemporaryFile("w", suffix=".json", delete=False) as tmp:
            json.dump(payload, tmp)
            path = tmp.name

        loaded = load_config(path)
        self.assertEqual(loaded, payload)

    def test_generate_parameter_combinations(self) -> None:
        params = {"a": [1, 2], "b": ["x", "y"], "c": 10}
        combos = generate_parameter_combinations(params)
        self.assertEqual(len(combos), 4)
        self.assertIn({"a": 1, "b": "x", "c": 10}, combos)
        self.assertIn({"a": 2, "b": "y", "c": 10}, combos)


if __name__ == "__main__":
    unittest.main()
