import pandas as pd
from .utilisation import generate_utilisation
from .parameters import get_parameters
from .annual_estimate import recalculate_annual_estimate
from time import sleep

def build_counter_data(config: dict):
    """Run a Monte Carlo simulation for SAP maintenance planning."""

    # Generate utilisation: shape (num_simulations, num_assets, num_days)
    utilisation = generate_utilisation(
        config["daily_utilisations"],
        config["num_simulations"],
        config["num_days"]
    )

    # Get SAP parameters (placeholder)
    # params = get_parameters(config["parameters"])

    # Prepare MultiIndex for simulation x asset x day
    num_sim = config["num_simulations"]
    num_days = config["num_days"]

    index = pd.MultiIndex.from_product(
        [range(num_sim), range(num_days)],
        names=["simulation", "day"]
    )

    # Flatten utilisation and create DataFrame
    df = pd.DataFrame({"utilisation": utilisation.reshape(-1)}, index=index)

    # Compute cumulative utilisation per simulation and asset
    df["cumulative_utilisation"] = df.groupby(
        "simulation")["utilisation"].cumsum()
    # Compute daily average utilisation per simulation if needed
    # daily_avg = df.groupby(["simulation", "day"]).mean().rename(columns={"utilisation": "avg_utilisation"})

    # print(df)
    return df


def build_work_order_schedule(parameter_config: dict) -> pd.DataFrame:
    """
    Pre-build a work order schedule from SAP parameter configuration.
    Expands items, cycles, and parameter combinations into a long-form DataFrame.
    """
    # Extract parameters
    annual_estimate = parameter_config.get("annual_estimate", 0)
    suppressed = parameter_config.get("suppressed", False)
    completion_requirement = parameter_config.get(
        "completion_requirement", True)
    early_shift_factors = parameter_config.get("early_shift_factors", 0)
    late_shift_factors = parameter_config.get("late_shift_factors", 0)
    call_horizon_days = parameter_config.get("call_horizon_days", 0)
    package_cycle = parameter_config.get("package_cycle", 0)
    items = parameter_config.get("items", {})
    

    records = []

    # Build all combinations of shift factors and horizon
    if not suppressed:
        for item, cycle in items.items():
            call_counter = cycle
            for call_number in range(1, 25):
                records.append({
                    "item": item,
                    "cycle": cycle,
                    "package_cycle": package_cycle,
                    "call_number": call_number,
                    "next_planned_counter": call_counter,
                    "planned_day": None,
                    "call_day": None,
                    "work_order_number": None,
                    "completion_day": None,
                    "completion_counter": None,
                    "annual_estimate": annual_estimate,
                    "suppressed": suppressed,
                    "completion_requirement": completion_requirement,
                    "early_shift": early_shift_factors,
                    "late_shift": late_shift_factors,
                    "call_horizon_days": call_horizon_days,
                    "units_prior_for_call": round(annual_estimate / 365 * call_horizon_days, 0),
                    "called": False,
                    "completion": False
                })
                call_counter += cycle

    if suppressed:
        for item, cycle in items.items():
            call_counter = cycle
            for call_number in range(1, 25):
                records.append({
                    "item": item,
                    "cycle": cycle,
                    "package_cycle": package_cycle,
                    "call_number": call_number,
                    "next_planned_counter": call_counter,
                    "planned_day": None,
                    "call_day": None,
                    "work_order_number": None,
                    "completion_day": None,
                    "completion_counter": None,
                    "annual_estimate": annual_estimate,
                    "suppressed": suppressed,
                    "completion_requirement": completion_requirement,
                    "early_shift": early_shift_factors,
                    "late_shift": late_shift_factors,
                    "call_horizon_days": call_horizon_days,
                    "units_prior_for_call": round(annual_estimate / 365 * call_horizon_days, 0),
                    "called": False,
                    "completion": False
                })
                call_counter += cycle

    work_order_df = pd.DataFrame.from_records(records)

    if not suppressed:
        # Sort by call_counter, then cycle, then item
        work_order_df = work_order_df.sort_values(
            by=["call_counter", "cycle"]
        ).reset_index(drop=True)

        # Global sequential numbering
        work_order_df["call_number"] = range(1, len(work_order_df) + 1)

    if suppressed:
        # drop duplicates based on call_counter, keeping the one with the largest cycle
        work_order_df = work_order_df.sort_values(
            by=["next_planned_counter", "cycle"], ascending=[True, False]
        ).drop_duplicates(subset=["next_planned_counter"]).reset_index(drop=True)
        # Global sequential numbering
        work_order_df["call_number"] = range(1, len(work_order_df) + 1)

    # Assuming work_order_df is built and sorted
    min_cycle = work_order_df['cycle'].min()
    last_index = work_order_df[work_order_df['cycle'] == min_cycle].index[-1]

    filtered_df = work_order_df.loc[:last_index - 1].copy()
    filtered_df = filtered_df.reset_index(drop=True)
    filtered_df["call_number"] = range(1, len(filtered_df) + 1)
    filtered_df["call_counter"] = filtered_df["next_planned_counter"] - \
        filtered_df["units_prior_for_call"]
    filtered_df["last_completion_counter"] = 0
    filtered_df["last_completion_counter_item"] = 0
    filtered_df["last_completion_counter_var"] = 0
    filtered_df['open_work_orders'] = False
    filtered_df['next_call_number'] = 1
    filtered_df['last_completed_call_number'] = 0

    return filtered_df


def run_simulation(df: pd.DataFrame, parameter_config: dict) -> pd.DataFrame:
    """
    Run a simulation on utilisation data given a specific parameter set.

    df: DataFrame with MultiIndex (simulation, day) and columns:
        - utilisation
        - cumulative_utilisation
    parameter_config: dict containing one combination of simulation parameters

    Returns updated df with new columns for simulation logic.
    """
    # Copy df to avoid modifying the original
    df = df.copy()

    work_order_df = build_work_order_schedule(parameter_config)

    # Extract parameters for easier access
    annual_estimate = work_order_df['annual_estimate'].iloc[0]
    recalc_days = work_order_df['annual_estimate_recalculate_after_days'].iloc[
        0] if 'annual_estimate_recalculate_after_days' in work_order_df else 100
    suppressed = work_order_df['suppressed'].iloc[0] if 'suppressed' in work_order_df else False
    completion_requirement = work_order_df['completion_requirement'].iloc[
        0] if 'completion_requirement' in work_order_df else True
    early_shift_factors = work_order_df['early_shift_factors'].iloc[0] if 'early_shift_factors' in work_order_df else 0
    late_shift_factors = work_order_df['late_shift_factors'].iloc[0] if 'late_shift_factors' in work_order_df else 0
    call_horizon_days = work_order_df['call_horizon_days'].iloc[0] if 'call_horizon_days' in work_order_df else 0
    package_cycle = work_order_df['package_cycle'].iloc[0] if 'package_cycle' in work_order_df else 0

    work_order_dfs = []

    def adjust_unit_prior_for_call(work_order_df, units_prior_for_call):
        work_order_df.loc[work_order_df['called'] == False, 'units_prior_for_call'] = units_prior_for_call
        df = recalculate_calls(work_order_df)
        return df

    def recalculate_calls(work_order_df):
        # Logic to recalculate calls based on units_prior_for_call
    
        def _row_logic(row):
            if not row['called']:
                recal = False

                # Determine recalculation trigger
                if row['completion_requirement'] and not row['open_work_orders']:
                    if row['call_number'] == row['next_call_number']:
                        recal = True

                # Proceed if no completion requirement or recal triggered
                if not row['completion_requirement'] or recal:
                    # Determine last counter
                    last = row['last_completion_counter'] if row['suppressed'] else row['last_completion_counter_item']
                    last_counter = last if last != 0 else row['next_planned_counter'] - row['package_cycle']

                    # Adjust next planned counter
                    if row['call_number'] >= row['next_call_number']:
                        diff = row['call_number'] - row['last_completed_call_number']
                        var = row['last_completion_counter_var']

                        if var > 0:
                            if row['late_shift'] == 1:
                                row['next_planned_counter'] = last_counter + (row['package_cycle'] * diff)
                            elif 0 < row['late_shift'] < 1:
                                row['next_planned_counter'] = last_counter + (row['package_cycle'] * diff) - \
                                    row['late_shift'] * var
                            else:
                                row['next_planned_counter'] = last_counter + (row['package_cycle'] * diff)

                        elif var < 0:
                            if row['early_shift'] == 1:
                                row['next_planned_counter'] = last_counter + (row['package_cycle'] * diff)
                            elif 0 < row['early_shift'] < 1:
                                row['next_planned_counter'] = last_counter + (row['package_cycle'] * diff) + \
                                    row['early_shift'] * abs(var)
                            else:
                                row['next_planned_counter'] = last_counter + (row['package_cycle'] * diff)

                    # Final counter calc
                    row['call_counter'] = row['next_planned_counter'] - row['units_prior_for_call']

            return row

        
        # determine if any open work orders        
        work_order_df['open_work_orders'] = ((work_order_df['called']) & (~work_order_df['completion'])).any()
        
        # get the next call number to be called if there is no open work orders
        work_order_df = work_order_df.apply(_row_logic, axis=1)
        # work_order_df['call_counter'] = work_order_df['next_planned_counter'] - \
        #     work_order_df['units_prior_for_call']
        
        work_order_df.to_csv(f'work_order_sim_{sim}.csv', index=False)
        # sleep(.3)
        return work_order_df
    
    def initialize_call_completion_sets(work_order_df):
        # create sets for call_counters and completion_days, with call numbers for tracking
        completion_days = [
            (call_number, planned_day)
            for call_number, planned_day, called, completed in zip(
                work_order_df['call_number'],
                work_order_df['planned_day'],
                work_order_df['called'],
                work_order_df['completion']
            )
            if called and not completed
        ]

        call_counters = [
            (call_number, call_counter)
            for call_number, call_counter, called in zip(
                work_order_df['call_number'],
                work_order_df['call_counter'],
                work_order_df['called']
            )
            if not called
        ]
        return call_counters, completion_days
        
    

    def call_work_order(work_order_df, day, call_counter, call_number):
        mask = (work_order_df["call_counter"] < call_counter) & (
            work_order_df["call_day"].isna())
        work_order_df.loc[mask, "call_day"] = day
        work_order_df.loc[mask, "planned_day"] = day + call_horizon_days
        work_order_df.loc[mask,
                          "work_order_number"] = work_order_df.index[mask] + 1
        work_order_df.loc[mask, "called"] = True
        work_order_df["next_call_number"] = call_number + 1
        df = recalculate_calls(work_order_df)
        return df
    
    def complete_work_order(work_order_df, day, call, counter):
        work_order_df.loc[work_order_df['call_number']
                          == call, 'completion_day'] = day
        work_order_df.loc[work_order_df['call_number']
                          == call, 'completion_counter'] = counter
        work_order_df.loc[work_order_df['call_number']
                          == call, 'completion'] = True

        # work_order_df['last_completion_counter'] = counter
        
        # Grab the single value safely
        planned = work_order_df.loc[work_order_df['call_number'] == call, 'next_planned_counter']
        if not planned.empty:
            work_order_df['last_completion_counter_var'] = planned.iloc[0] - counter

        item = work_order_df.loc[work_order_df['call_number']
                                 == call, 'item'].values[0]
        
        work_order_df['last_completion_counter_item'] = work_order_df['last_completion_counter_item'].astype(float)

        work_order_df.loc[work_order_df['item'] == item, 'last_completion_counter_item'] = counter.astype(float)

        
        work_order_df['last_completion_counter'] = counter
        work_order_df['last_completed_call_number'] = call
        df = recalculate_calls(work_order_df)

        return df

    for sim in df.index.get_level_values("simulation").unique():
        sim_df = df.loc[sim]
        current_work_order_number = 1
        units_prior_for_call = 0
        call_counters = []
        completion_days = []

        sim_work_order_df = work_order_df.copy()
        sim_work_order_df['simulation'] = sim
        print(sim_df.index)
        for day in sim_df.index:
            sleep(0.01)
            cumulative = df.loc[(sim, day), "cumulative_utilisation"]
            if day % 7 == 0:
                sim_work_order_df = recalculate_calls(sim_work_order_df)
                call_counters, completion_days = initialize_call_completion_sets(
                    sim_work_order_df)
            
            # recalculate annual estimate if needed
            if day % recalc_days == 0:
                # sleep(1)
                print('Recalculating annual estimate on day', day)
                start_day = max(1, day - 29)  # avoid negative or zero days
                cumulative_list = sim_df.loc[start_day:day, "utilisation"].tolist()
                annual_estimate = recalculate_annual_estimate(cumulative_list)
                sim_work_order_df.loc[sim_work_order_df['called'] == False, 'annual_estimate'] = annual_estimate
                units_prior_for_call = annual_estimate / 365 * call_horizon_days
                sim_work_order_df = adjust_unit_prior_for_call(
                    sim_work_order_df, units_prior_for_call)

                call_counters, completion_days = initialize_call_completion_sets(
                    sim_work_order_df)
            
            # Check if we need to call a work order
            for call, call_counter in call_counters:
                if cumulative > call_counter:
                    sleep(1)
                    print('Calling work order', call, 'on day', day, 'cumulative:', cumulative)
                    sim_work_order_df = call_work_order(
                        sim_work_order_df, day, cumulative, call)
                    call_counters, completion_days = initialize_call_completion_sets(
                        sim_work_order_df)
                    # sleep(30)                    

            # Check if we need to complete a work order
            for call, planned_day in completion_days:
                if day == planned_day:
                    sleep(1)
                    print('Completing work order', call, 'on day', day, 'cumulative:', cumulative)
                    sim_work_order_df = complete_work_order(
                        sim_work_order_df, day, call, cumulative)
                    call_counters, completion_days = initialize_call_completion_sets(
                        sim_work_order_df)
                    
            print('end of day:', day, 'sim:', sim, 'counter:', cumulative)# 'call_counters:', call_counters, 'completion_days:', completion_days)
        print(sim_work_order_df)
        sim_work_order_df.to_csv(f'work_order_sim_{sim}.csv', index=False)
    # print(df)
    return sim_work_order_df
