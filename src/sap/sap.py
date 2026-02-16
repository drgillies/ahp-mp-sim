from typing import Any

import pandas as pd

from src.sap.annual_estimate import recalculate_annual_estimate
from src.utils.numbers import resolve_positive_int


class SAP:
    """Stateful SAP maintenance-plan model used by simulation."""

    def __init__(self, parameter_config: dict[str, Any]) -> None:
        self.parameter_config = parameter_config
        self.annual_estimate = float(parameter_config.get("annual_estimate", 0))
        self.recalc_days = resolve_positive_int(
            parameter_config.get("annual_estimate_recalculate_after_days", 100)
        )
        self.suppressed = bool(parameter_config.get("suppressed", False))
        self.completion_requirement = bool(
            parameter_config.get("completion_requirement", True)
        )
        self.early_shift = float(parameter_config.get("early_shift_factors", 0))
        self.late_shift = float(parameter_config.get("late_shift_factors", 0))
        self.call_horizon_days = int(parameter_config.get("call_horizon_days", 0))
        self.package_cycle = float(parameter_config.get("package_cycle", 0))
        self.items = parameter_config.get("items", {})

    def build_work_order_schedule(self) -> pd.DataFrame:
        """Build work-order rows from configured maintenance-plan parameters."""
        records: list[dict[str, Any]] = []
        for item, cycle in self.items.items():
            call_counter = float(cycle)
            for call_number in range(1, 25):
                records.append(
                    {
                        "item": item,
                        "cycle": float(cycle),
                        "package_cycle": self.package_cycle,
                        "call_number": call_number,
                        "next_planned_counter": call_counter,
                        "planned_day": None,
                        "call_day": None,
                        "work_order_number": None,
                        "completion_day": None,
                        "completion_counter": None,
                        "annual_estimate": self.annual_estimate,
                        "annual_estimate_recalculate_after_days": self.recalc_days,
                        "suppressed": self.suppressed,
                        "completion_requirement": self.completion_requirement,
                        "early_shift": self.early_shift,
                        "late_shift": self.late_shift,
                        "call_horizon_days": self.call_horizon_days,
                        "units_prior_for_call": round(
                            (self.annual_estimate / 365) * self.call_horizon_days, 0
                        ),
                        "called": False,
                        "completion": False,
                    }
                )
                call_counter += float(cycle)

        work_order_df = pd.DataFrame.from_records(records)
        if work_order_df.empty:
            return work_order_df

        if self.suppressed:
            work_order_df = (
                work_order_df.sort_values(
                    by=["next_planned_counter", "cycle"], ascending=[True, False]
                )
                .drop_duplicates(subset=["next_planned_counter"])
                .reset_index(drop=True)
            )
        else:
            work_order_df = work_order_df.sort_values(
                by=["next_planned_counter", "cycle", "item"]
            ).reset_index(drop=True)

        work_order_df["call_number"] = range(1, len(work_order_df) + 1)

        min_cycle = work_order_df["cycle"].min()
        last_index = work_order_df[work_order_df["cycle"] == min_cycle].index[-1]
        filtered_df = work_order_df.iloc[:last_index].copy()

        filtered_df = filtered_df.reset_index(drop=True)
        filtered_df["call_number"] = range(1, len(filtered_df) + 1)
        filtered_df["call_counter"] = (
            filtered_df["next_planned_counter"] - filtered_df["units_prior_for_call"]
        )
        filtered_df["last_completion_counter"] = 0.0
        filtered_df["last_completion_counter_item"] = 0.0
        filtered_df["last_completion_counter_var"] = 0.0
        filtered_df["open_work_orders"] = False
        filtered_df["next_call_number"] = 1
        filtered_df["last_completed_call_number"] = 0

        return filtered_df

    def recalculate_plan_calls(self, work_order_df: pd.DataFrame) -> pd.DataFrame:
        """Recalculate call counters and shifted planned counters for open plan rows."""
        work_order_df = work_order_df.copy()
        open_orders = bool(
            ((work_order_df["called"]) & (~work_order_df["completion"])).any()
        )
        work_order_df["open_work_orders"] = open_orders

        def _row_logic(row: pd.Series) -> pd.Series:
            if row["called"]:
                return row

            recal = (
                row["completion_requirement"]
                and not row["open_work_orders"]
                and row["call_number"] == row["next_call_number"]
            )
            if row["completion_requirement"] and not recal:
                return row

            last = (
                row["last_completion_counter"]
                if row["suppressed"]
                else row["last_completion_counter_item"]
            )
            last_counter = (
                last if last != 0 else row["next_planned_counter"] - row["package_cycle"]
            )

            if row["call_number"] >= row["next_call_number"]:
                diff = row["call_number"] - row["last_completed_call_number"]
                var = row["last_completion_counter_var"]
                shifted_counter = last_counter + (row["package_cycle"] * diff)

                if var > 0 and 0 < row["late_shift"] < 1:
                    shifted_counter -= row["late_shift"] * var
                elif var < 0 and 0 < row["early_shift"] < 1:
                    shifted_counter += row["early_shift"] * abs(var)

                row["next_planned_counter"] = shifted_counter

            row["call_counter"] = row["next_planned_counter"] - row["units_prior_for_call"]
            return row

        return work_order_df.apply(_row_logic, axis=1)

    def initialize_call_completion_sets(
        self, work_order_df: pd.DataFrame
    ) -> tuple[list[tuple[int, float]], list[tuple[int, int]]]:
        """Get callable work orders and completion targets from current plan state."""
        completion_days = [
            (int(call_number), int(planned_day))
            for call_number, planned_day, called, completed in zip(
                work_order_df["call_number"],
                work_order_df["planned_day"],
                work_order_df["called"],
                work_order_df["completion"],
            )
            if called and (not completed) and pd.notna(planned_day)
        ]

        call_counters = [
            (int(call_number), float(call_counter))
            for call_number, call_counter, called in zip(
                work_order_df["call_number"],
                work_order_df["call_counter"],
                work_order_df["called"],
            )
            if not called
        ]
        return call_counters, completion_days

    def call_work_order(
        self,
        work_order_df: pd.DataFrame,
        day: int,
        current_counter: float,
        call_number: int,
    ) -> pd.DataFrame:
        """Call eligible work orders and set planned completion day."""
        mask = (work_order_df["call_counter"] < current_counter) & (
            work_order_df["call_day"].isna()
        )
        work_order_df.loc[mask, "call_day"] = day
        work_order_df.loc[mask, "planned_day"] = day + self.call_horizon_days
        work_order_df.loc[mask, "work_order_number"] = work_order_df.index[mask] + 1
        work_order_df.loc[mask, "called"] = True
        work_order_df["next_call_number"] = call_number + 1
        return self.recalculate_plan_calls(work_order_df)

    def execute_work_order(
        self, work_order_df: pd.DataFrame, day: int, call_number: int, counter: float
    ) -> pd.DataFrame:
        """Execute one work order and update completion-driven SAP plan state."""
        mask = work_order_df["call_number"] == call_number
        if not mask.any():
            return work_order_df

        counter_value = float(counter)
        work_order_df.loc[mask, "completion_day"] = day
        work_order_df.loc[mask, "completion_counter"] = counter_value
        work_order_df.loc[mask, "completion"] = True

        planned_counter = float(work_order_df.loc[mask, "next_planned_counter"].iloc[0])
        work_order_df["last_completion_counter_var"] = planned_counter - counter_value

        item = work_order_df.loc[mask, "item"].iloc[0]
        work_order_df["last_completion_counter_item"] = work_order_df[
            "last_completion_counter_item"
        ].astype(float)
        work_order_df.loc[
            work_order_df["item"] == item, "last_completion_counter_item"
        ] = counter_value

        work_order_df["last_completion_counter"] = counter_value
        work_order_df["last_completed_call_number"] = int(call_number)
        return self.recalculate_plan_calls(work_order_df)

    def refresh_annual_estimate_for_open_orders(
        self,
        work_order_df: pd.DataFrame,
        utilisation_slice: list[float],
        call_horizon_days: int | None = None,
    ) -> pd.DataFrame:
        """Recalculate annual estimate and units-prior for not-yet-called work orders."""
        annual_estimate = recalculate_annual_estimate(utilisation_slice)
        horizon = call_horizon_days if call_horizon_days is not None else self.call_horizon_days
        work_order_df.loc[work_order_df["called"] == False, "annual_estimate"] = (
            annual_estimate
        )
        work_order_df.loc[work_order_df["called"] == False, "units_prior_for_call"] = (
            annual_estimate / 365
        ) * horizon
        return self.recalculate_plan_calls(work_order_df)
