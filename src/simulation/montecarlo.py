from pathlib import Path
from typing import Any

import pandas as pd

from .annual_estimate import recalculate_annual_estimate
from .utilisation import generate_utilisation
from src.utils.numbers import resolve_positive_int


def build_counter_data(config: dict[str, Any]) -> pd.DataFrame:
    """Generate utilisation and cumulative counters per simulation/day."""
    utilisation = generate_utilisation(
        config["daily_utilisations"],
        config["num_simulations"],
        config["num_days"],
    )

    index = pd.MultiIndex.from_product(
        [range(config["num_simulations"]), range(config["num_days"])],
        names=["simulation", "day"],
    )

    df = pd.DataFrame({"utilisation": utilisation.reshape(-1)}, index=index)
    df["cumulative_utilisation"] = df.groupby("simulation")["utilisation"].cumsum()
    return df


def build_work_order_schedule(parameter_config: dict[str, Any]) -> pd.DataFrame:
    """
    Build work-order rows from parameter config.
    """
    annual_estimate = float(parameter_config.get("annual_estimate", 0))
    recalc_days = resolve_positive_int(
        parameter_config.get("annual_estimate_recalculate_after_days", 100)
    )
    suppressed = bool(parameter_config.get("suppressed", False))
    completion_requirement = bool(parameter_config.get("completion_requirement", True))
    early_shift = float(parameter_config.get("early_shift_factors", 0))
    late_shift = float(parameter_config.get("late_shift_factors", 0))
    call_horizon_days = int(parameter_config.get("call_horizon_days", 0))
    package_cycle = float(parameter_config.get("package_cycle", 0))
    items = parameter_config.get("items", {})

    records: list[dict[str, Any]] = []
    for item, cycle in items.items():
        call_counter = float(cycle)
        for call_number in range(1, 25):
            records.append(
                {
                    "item": item,
                    "cycle": float(cycle),
                    "package_cycle": package_cycle,
                    "call_number": call_number,
                    "next_planned_counter": call_counter,
                    "planned_day": None,
                    "call_day": None,
                    "work_order_number": None,
                    "completion_day": None,
                    "completion_counter": None,
                    "annual_estimate": annual_estimate,
                    "annual_estimate_recalculate_after_days": recalc_days,
                    "suppressed": suppressed,
                    "completion_requirement": completion_requirement,
                    "early_shift": early_shift,
                    "late_shift": late_shift,
                    "call_horizon_days": call_horizon_days,
                    "units_prior_for_call": round(
                        (annual_estimate / 365) * call_horizon_days, 0
                    ),
                    "called": False,
                    "completion": False,
                }
            )
            call_counter += float(cycle)

    work_order_df = pd.DataFrame.from_records(records)
    if work_order_df.empty:
        return work_order_df

    if suppressed:
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


def run_simulation(
    df: pd.DataFrame,
    parameter_config: dict[str, Any],
    export_csv: bool = True,
    output_dir: str = ".",
) -> pd.DataFrame:
    """
    Run simulation against utilisation/cumulative counter data.
    """
    df = df.copy()
    base_work_order_df = build_work_order_schedule(parameter_config)
    if base_work_order_df.empty:
        return base_work_order_df

    call_horizon_days = int(base_work_order_df["call_horizon_days"].iloc[0])
    recalc_days = resolve_positive_int(
        base_work_order_df["annual_estimate_recalculate_after_days"].iloc[0]
    )
    all_simulation_results: list[pd.DataFrame] = []

    def recalculate_calls(work_order_df: pd.DataFrame) -> pd.DataFrame:
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
        work_order_df: pd.DataFrame,
    ) -> tuple[list[tuple[int, float]], list[tuple[int, int]]]:
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
        work_order_df: pd.DataFrame,
        day: int,
        current_counter: float,
        call_number: int,
    ) -> pd.DataFrame:
        mask = (work_order_df["call_counter"] < current_counter) & (
            work_order_df["call_day"].isna()
        )
        work_order_df.loc[mask, "call_day"] = day
        work_order_df.loc[mask, "planned_day"] = day + call_horizon_days
        work_order_df.loc[mask, "work_order_number"] = work_order_df.index[mask] + 1
        work_order_df.loc[mask, "called"] = True
        work_order_df["next_call_number"] = call_number + 1
        return recalculate_calls(work_order_df)

    def complete_work_order(
        work_order_df: pd.DataFrame, day: int, call_number: int, counter: float
    ) -> pd.DataFrame:
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
        return recalculate_calls(work_order_df)

    for sim in df.index.get_level_values("simulation").unique():
        sim_df = df.loc[sim]
        sim_work_order_df = recalculate_calls(base_work_order_df.copy())
        sim_work_order_df["simulation"] = sim
        call_counters, completion_days = initialize_call_completion_sets(sim_work_order_df)

        for day in sim_df.index:
            cumulative = float(df.loc[(sim, day), "cumulative_utilisation"])

            if day % 7 == 0:
                sim_work_order_df = recalculate_calls(sim_work_order_df)
                call_counters, completion_days = initialize_call_completion_sets(
                    sim_work_order_df
                )

            if day % recalc_days == 0:
                start_day = max(0, day - 29)
                utilisation_slice = sim_df.loc[start_day:day, "utilisation"].tolist()
                annual_estimate = recalculate_annual_estimate(utilisation_slice)
                sim_work_order_df.loc[
                    sim_work_order_df["called"] == False, "annual_estimate"
                ] = annual_estimate
                units_prior_for_call = (annual_estimate / 365) * call_horizon_days
                sim_work_order_df.loc[
                    sim_work_order_df["called"] == False, "units_prior_for_call"
                ] = units_prior_for_call
                sim_work_order_df = recalculate_calls(sim_work_order_df)
                call_counters, completion_days = initialize_call_completion_sets(
                    sim_work_order_df
                )

            for call_number, call_counter in list(call_counters):
                if cumulative > call_counter:
                    sim_work_order_df = call_work_order(
                        sim_work_order_df, day, cumulative, call_number
                    )
                    call_counters, completion_days = initialize_call_completion_sets(
                        sim_work_order_df
                    )

            for call_number, planned_day in list(completion_days):
                if day == planned_day:
                    sim_work_order_df = complete_work_order(
                        sim_work_order_df, day, call_number, cumulative
                    )
                    call_counters, completion_days = initialize_call_completion_sets(
                        sim_work_order_df
                    )

        all_simulation_results.append(sim_work_order_df)
        if export_csv:
            destination = Path(output_dir) / f"work_order_sim_{sim}.csv"
            sim_work_order_df.to_csv(destination, index=False)

    return pd.concat(all_simulation_results, ignore_index=True)
