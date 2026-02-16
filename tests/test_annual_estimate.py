import unittest

from src.simulation.annual_estimate import recalculate_annual_estimate


class AnnualEstimateTests(unittest.TestCase):
    def test_recalculate_annual_estimate_from_values(self) -> None:
        values = [1, 2, 3]
        result = recalculate_annual_estimate(values)
        self.assertEqual(result, 730.0)

    def test_recalculate_annual_estimate_empty(self) -> None:
        self.assertEqual(recalculate_annual_estimate([]), 0)


if __name__ == "__main__":
    unittest.main()
