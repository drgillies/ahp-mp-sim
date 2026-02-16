# Runbook

## Prerequisites

- Python 3.10+ recommended
- `uv` installed

## Environment Setup

Create environment:

```bash
uv venv .venv
```

Install dependencies:

```bash
uv pip install -r requirements.txt
```

## Run

From project root:

```bash
uv run python main.py
```

Generate last-run reports:

```bash
uv run python last_run_report.py
```

## Current Runtime Behavior

- Loads `config.json`
- Builds utilisation and cumulative counters
- Generates parameter combinations
- Runs simulation for the first parameter combination only
- Filters to completed work orders
- Plots:
  - `call_number` vs `next_planned_counter`
  - `call_number` vs cumulative package cycle

## Outputs

- CSV files:
  - `work_order_sim_0.csv` (and additional IDs when multiple simulations are run)
  - Note: this default location comes from current `main.py` usage of `run_simulation(...)`.
- Report files:
  - `reports/last_run_report.md`
  - `reports/last_run_report.html`
  - `reports/last_run_assets/*.png`
- Matplotlib window when plotting enabled

## Configuration Notes

- `daily_utilisations` phases are applied by increasing `after_day`.
- List values in `parameters` are expanded into combinations.
- To change CSV output location, pass `output_dir` to `run_simulation(...)`.
