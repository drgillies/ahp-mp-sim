import unittest

from src.simulation.montecarlo import (
    build_counter_data,
    build_work_order_schedule,
    run_simulation,
)


class MonteCarloTests(unittest.TestCase):
    def test_build_work_order_schedule_non_suppressed(self) -> None:
        parameter_config = {
            "package_cycle": 2000,
            "items": {"replace couplings": 2000, "overhaul": 8000},
            "annual_estimate": 5000,
            "annual_estimate_recalculate_after_days": 30,
            "suppressed": False,
            "completion_requirement": False,
            "early_shift_factors": 0,
            "late_shift_factors": 0,
            "call_horizon_days": 30,
        }

        schedule_df = build_work_order_schedule(parameter_config)

        self.assertFalse(schedule_df.empty)
        self.assertIn("call_counter", schedule_df.columns)
        self.assertIn("annual_estimate_recalculate_after_days", schedule_df.columns)
        self.assertEqual(
            int(schedule_df["annual_estimate_recalculate_after_days"].iloc[0]), 30
        )

    def test_build_work_order_schedule_suppressed(self) -> None:
        parameter_config = {
            "package_cycle": 2000,
            "items": {"replace couplings": 2000, "overhaul": 8000},
            "annual_estimate": 5000,
            "annual_estimate_recalculate_after_days": 7,
            "suppressed": True,
            "completion_requirement": False,
            "early_shift_factors": 0,
            "late_shift_factors": 0,
            "call_horizon_days": 30,
        }

        schedule_df = build_work_order_schedule(parameter_config)

        self.assertFalse(schedule_df.empty)
        self.assertTrue(schedule_df["next_planned_counter"].is_unique)

    def test_run_simulation_returns_all_simulations_and_completions(self) -> None:
        config = {
            "num_simulations": 2,
            "num_days": 60,
            "daily_utilisations": {
                "base": {
                    "after_day": 0,
                    "distribution": "uniform",
                    "min": 5,
                    "max": 5,
                }
            },
        }
        parameter_config = {
            "package_cycle": 20,
            "items": {"replace couplings": 20, "overhaul": 40},
            "annual_estimate": 365,
            "annual_estimate_recalculate_after_days": 7,
            "suppressed": False,
            "completion_requirement": False,
            "early_shift_factors": 0,
            "late_shift_factors": 0,
            "call_horizon_days": 1,
        }

        counter_df = build_counter_data(config)
        result_df = run_simulation(counter_df, parameter_config, export_csv=False)

        self.assertEqual(set(result_df["simulation"].unique()), {0, 1})
        self.assertTrue(result_df["completion"].any())
        completion_values = result_df.loc[
            result_df["completion"] == True, "completion_counter"
        ]
        self.assertTrue(completion_values.notna().all())


if __name__ == "__main__":
    unittest.main()
