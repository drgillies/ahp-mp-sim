import unittest

from simulation.config_loader import generate_parameter_combinations
from simulation.montecarlo import build_counter_data


class SmokeTests(unittest.TestCase):
    def test_generate_parameter_combinations(self) -> None:
        params = {
            "a": [1, 2],
            "b": ["x", "y"],
            "c": 10,
        }
        combos = generate_parameter_combinations(params)
        self.assertEqual(len(combos), 4)
        self.assertTrue(all(combo["c"] == 10 for combo in combos))

    def test_build_counter_data_shape(self) -> None:
        config = {
            "num_simulations": 2,
            "num_days": 5,
            "daily_utilisations": {
                "base": {
                    "after_day": 0,
                    "distribution": "uniform",
                    "min": 1,
                    "max": 1,
                }
            },
        }
        df = build_counter_data(config)
        self.assertEqual(len(df), 10)
        self.assertIn("cumulative_utilisation", df.columns)


if __name__ == "__main__":
    unittest.main()
