# Project Overview

## Project Name

AHP MP Simulation

## Purpose

This project simulates maintenance planning behavior against a synthetic utilisation signal. It is intended to model how call timing, completion timing, and planning parameters influence work order outcomes over time.

## Primary Goals

- Generate day-by-day utilisation profiles from configurable distributions.
- Build a maintenance schedule from planning parameters.
- Simulate work order call and completion events based on counters and horizons.
- Recalculate annual estimate values during simulation and propagate their impact.
- Visualize selected result signals for quick inspection.

## Current Entry Point

- `main.py`

`main.py` loads `config.json`, builds counter data, runs one parameter combination, filters completed orders, calculates a cumulative package-cycle series, and plots counters.

## Current Deliverables

- In-memory pandas DataFrames for utilisation and work-order state.
- CSV exports per simulation in the project root:
  - `work_order_sim_<simulation_id>.csv`
- Optional matplotlib plot for call progression.

## Intended Audience

- Engineers validating maintenance-planning logic.
- Analysts exploring parameter sensitivity.
- Developers extending scheduling or simulation rules.
