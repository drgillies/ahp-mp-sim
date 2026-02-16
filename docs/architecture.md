# Architecture

## Repository Structure

- `main.py`: Program entrypoint and plotting workflow.
- `last_run_report.py`: Builds last-run markdown and HTML reports with visuals.
- `config.json`: Runtime configuration.
- `src/simulation/config_loader.py`: Config loading and parameter combination generation.
- `src/simulation/utilisation.py`: Daily utilisation generator by phase/distribution.
- `src/simulation/montecarlo.py`: Counter-data build, schedule creation, and simulation loop.
- `src/simulation/annual_estimate.py`: Annual estimate recalculation helper.
- `src/simulation/parameters.py`: Parameter extraction helper.
- `src/simulation/results.py`: Basic summary helper.
- `src/utils/json_io.py`: Shared JSON file loading helper.
- `src/utils/combinatorics.py`: Shared cartesian-combination helper.
- `src/utils/numbers.py`: Shared numeric parsing and validation helper.

## Data Flow

1. `main.py` loads config with `load_config`.
2. `build_counter_data` generates utilisation and cumulative counters per simulation/day.
3. Parameter combinations are built by `generate_parameter_combinations`.
4. `run_simulation`:
   - builds work-order schedule
   - iterates day-by-day for each simulation
   - recalculates calls and annual estimates on cadence
   - marks call/completion transitions
   - writes simulation CSV output (default: project root unless `output_dir` is provided)
5. `main.py` filters completed rows and plots selected columns.
6. `last_run_report.py` reads the latest run CSV (prefers `data/`, then root), and writes reports into `reports/`.

## Core Data Entities

- Utilisation DataFrame (indexed by `simulation`, `day`):
  - `utilisation`
  - `cumulative_utilisation`
- Work-order DataFrame:
  - identifying columns: `item`, `cycle`, `call_number`
  - planning columns: `next_planned_counter`, `call_counter`, `planned_day`
  - execution columns: `called`, `call_day`, `completion`, `completion_day`, `completion_counter`
  - state-tracking columns: `last_completion_counter*`, `next_call_number`

## Configuration Highlights

Top-level:

- `num_simulations`
- `num_days`
- `daily_utilisations`
- `parameters`

Expandable list parameters in `parameters` become cartesian combinations.

## Current Design Constraints

- Heavy logic is concentrated in `src/simulation/montecarlo.py`.
- Recalculation logic is row-wise (`DataFrame.apply`) and may be slow for very large runs.
