import unittest

import numpy as np

from src.simulation.utilisation import generate_utilisation


class UtilisationTests(unittest.TestCase):
    def test_generate_utilisation_shape_and_bounds(self) -> None:
        np.random.seed(1)
        dist_cfg = {
            "phase_1": {
                "after_day": 0,
                "distribution": "normal",
                "mean": 5,
                "std": 2,
                "min": 0,
                "max": 10,
            },
            "phase_2": {
                "after_day": 5,
                "distribution": "uniform",
                "min": 2,
                "max": 4,
            },
        }

        arr = generate_utilisation(dist_cfg, num_simulations=3, num_days=10)

        self.assertEqual(arr.shape, (3, 10))
        self.assertGreaterEqual(arr.min(), 0)
        self.assertLessEqual(arr.max(), 10)

    def test_generate_utilisation_unsupported_distribution(self) -> None:
        dist_cfg = {
            "phase_1": {
                "after_day": 0,
                "distribution": "invalid",
            }
        }
        with self.assertRaises(ValueError):
            generate_utilisation(dist_cfg, num_simulations=1, num_days=3)


if __name__ == "__main__":
    unittest.main()
