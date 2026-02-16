from pathlib import Path
from typing import Any

import pandas as pd

from src.sap.sap import SAP
from .utilisation import generate_utilisation


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
    """Build work-order rows from parameter config."""
    return SAP(parameter_config).build_work_order_schedule()


def run_simulation(
    df: pd.DataFrame,
    parameter_config: dict[str, Any],
    export_csv: bool = True,
    output_dir: str = ".",
) -> pd.DataFrame:
    """Run simulation against utilisation/cumulative counter data."""
    df = df.copy()
    sap = SAP(parameter_config)
    base_work_order_df = sap.build_work_order_schedule()
    if base_work_order_df.empty:
        return base_work_order_df

    recalc_days = sap.recalc_days
    all_simulation_results: list[pd.DataFrame] = []

    for sim in df.index.get_level_values("simulation").unique():
        sim_df = df.loc[sim]
        sim_work_order_df = sap.recalculate_plan_calls(base_work_order_df.copy())
        sim_work_order_df["simulation"] = sim
        call_counters, completion_days = sap.initialize_call_completion_sets(
            sim_work_order_df
        )

        for day in sim_df.index:
            cumulative = float(df.loc[(sim, day), "cumulative_utilisation"])

            if day % 7 == 0:
                sim_work_order_df = sap.recalculate_plan_calls(sim_work_order_df)
                call_counters, completion_days = sap.initialize_call_completion_sets(
                    sim_work_order_df
                )

            if day % recalc_days == 0:
                start_day = max(0, day - 29)
                utilisation_slice = sim_df.loc[start_day:day, "utilisation"].tolist()
                sim_work_order_df = sap.refresh_annual_estimate_for_open_orders(
                    sim_work_order_df, utilisation_slice
                )
                call_counters, completion_days = sap.initialize_call_completion_sets(
                    sim_work_order_df
                )

            for call_number, call_counter in list(call_counters):
                if cumulative > call_counter:
                    sim_work_order_df = sap.call_work_order(
                        sim_work_order_df, day, cumulative, call_number
                    )
                    call_counters, completion_days = sap.initialize_call_completion_sets(
                        sim_work_order_df
                    )

            for call_number, planned_day in list(completion_days):
                if day == planned_day:
                    sim_work_order_df = sap.execute_work_order(
                        sim_work_order_df, day, call_number, cumulative
                    )
                    call_counters, completion_days = sap.initialize_call_completion_sets(
                        sim_work_order_df
                    )

        all_simulation_results.append(sim_work_order_df)
        if export_csv:
            destination = Path(output_dir) / f"work_order_sim_{sim}.csv"
            sim_work_order_df.to_csv(destination, index=False)

    return pd.concat(all_simulation_results, ignore_index=True)
