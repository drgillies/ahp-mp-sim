import unittest

from src.sap.sap import SAP


class SAPTests(unittest.TestCase):
    def test_sap_build_work_order_schedule(self) -> None:
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

        sap = SAP(parameter_config)
        schedule_df = sap.build_work_order_schedule()

        self.assertFalse(schedule_df.empty)
        self.assertIn("call_counter", schedule_df.columns)

    def test_sap_call_and_execute_work_order(self) -> None:
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

        sap = SAP(parameter_config)
        schedule_df = sap.build_work_order_schedule()
        call_number = int(schedule_df["call_number"].iloc[0])
        call_counter = float(schedule_df["call_counter"].iloc[0])

        called_df = sap.call_work_order(
            schedule_df, day=1, current_counter=call_counter + 1, call_number=call_number
        )
        self.assertTrue(bool(called_df["called"].any()))

        completed_df = sap.execute_work_order(
            called_df, day=2, call_number=call_number, counter=call_counter + 2
        )
        mask = completed_df["call_number"] == call_number
        self.assertTrue(bool(completed_df.loc[mask, "completion"].iloc[0]))
        self.assertIsNotNone(completed_df.loc[mask, "completion_counter"].iloc[0])

    def test_initialize_call_completion_sets(self) -> None:
        parameter_config = {
            "package_cycle": 20,
            "items": {"replace couplings": 20},
            "annual_estimate": 365,
            "annual_estimate_recalculate_after_days": 7,
            "suppressed": False,
            "completion_requirement": False,
            "early_shift_factors": 0,
            "late_shift_factors": 0,
            "call_horizon_days": 1,
        }
        sap = SAP(parameter_config)
        schedule_df = sap.build_work_order_schedule()
        call_counters, completion_days = sap.initialize_call_completion_sets(schedule_df)

        self.assertGreater(len(call_counters), 0)
        self.assertEqual(completion_days, [])


if __name__ == "__main__":
    unittest.main()
