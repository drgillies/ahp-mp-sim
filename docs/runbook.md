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

- Console logs from simulation loop
- CSV files:
  - `work_order_sim_0.csv` (and additional IDs when multiple simulations are run)
- Matplotlib window when plotting enabled

## Configuration Notes

- `daily_utilisations` phases are applied by increasing `after_day`.
- List values in `parameters` are expanded into combinations.
- Long simulations may run slowly due to current debug sleeps and frequent writes.
