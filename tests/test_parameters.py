import unittest

from src.simulation.parameters import get_parameters


class ParametersTests(unittest.TestCase):
    def test_get_parameters_with_defaults(self) -> None:
        params_cfg = {
            "items": {"replace couplings": 2000},
            "suppressed": True,
            "completion_requirement": False,
            "early_shift_factors": [0, 1],
            "late_shift_factors": [0, 1],
            "call_horizon_days": [30, 60],
        }

        result = get_parameters(params_cfg)

        self.assertEqual(result["items"], {"replace couplings": 2000})
        self.assertIsNone(result["basic_start_date"])
        self.assertEqual(result["annual_estimate_recalculate_after_days"], 100)

    def test_get_parameters_resolves_recalc_days(self) -> None:
        params_cfg = {
            "items": {"replace couplings": 2000},
            "suppressed": False,
            "completion_requirement": True,
            "early_shift_factors": 1,
            "late_shift_factors": 1,
            "call_horizon_days": 30,
            "annual_estimate_recalculate_after_days": [7, 30],
        }

        result = get_parameters(params_cfg)
        self.assertEqual(result["annual_estimate_recalculate_after_days"], 7)


if __name__ == "__main__":
    unittest.main()
