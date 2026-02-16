# Scope

## In Scope

- Monte Carlo-style daily utilisation generation for one or more simulations.
- Configuration-driven parameters via `config.json`.
- Work-order schedule creation from:
  - item cycles
  - package cycle
  - call horizon
  - suppression and completion requirement behavior
  - early/late shift factors
- Simulation loop that updates:
  - call state
  - planned/completion days
  - completion counters
  - recalculated annual estimates
- Export of simulation outputs for inspection.

## Out of Scope (Current State)

- Persistent storage beyond CSV export.
- API/server interface.
- GUI application.
- Authentication/authorization concerns.
- Full SAP integration.
- Production orchestration and deployment automation.

## Assumptions

- Counter increments are derived from synthetic utilisation samples.
- Planning logic is evaluated in discrete daily steps.
- Parameter combinations may be swept, but current `main.py` runs only the first combination.

## Non-Goals

- Exact replication of SAP transaction behavior.
- Financial optimization.
- Fleet-level multi-asset balancing logic.

## Scope Evolution Priorities

1. Stabilize simulation correctness and remove runtime defects.
2. Add deterministic test coverage for scheduling and counter logic.
3. Expand reporting outputs (KPIs and scenario comparisons).
