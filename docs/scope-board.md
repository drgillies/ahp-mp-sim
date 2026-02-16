# Scope Board

## Completion Metrics

- Total tickets: `16`
- Done: `6`
- In Progress: `0`
- To Do: `10`
- Overall completion: `37.5%`

Update these numbers whenever a ticket moves state.

## To Do

### Priority 1 - Foundation (Do First)

- [ ] `SC-013` SAP logic testing to validate desired behavior.
  - Done when: test coverage exists for SAP-specific planning logic paths and expected outputs are documented.
- [ ] `SC-015` Run multiple scenario ranges in one execution and show in report.
  - Done when: one run can execute a scenario sweep (example: no shift factors to 100% shift factors) and the report compares results.
- [ ] `SC-007` Run each scenario at least 100 times for reporting.
  - Done when: simulation execution supports batch run count and report inputs reflect all runs.

### Priority 2 - Scale and Efficiency

- [ ] `SC-014` Optimize report-data storage to avoid duplicate scenario reruns.
  - Done when: scenario run identity/dedup logic prevents re-execution of identical scenarios and reuses stored outputs.

### Priority 3 - Reporting Expansion

- [ ] `SC-011` Detailed report: individual run planned vs actual counter.
  - Done when: report supports selecting one run and rendering planned vs actual counter.
- [ ] `SC-012` Detailed report: individual counter variance by call.
  - Done when: report supports selecting one run and rendering counter variance by call.
- [ ] `SC-008` Multi-simulation report: call variance histogram.
  - Done when: report output includes a call variance histogram across simulation runs.
- [ ] `SC-009` Multi-simulation report: item counter variance histogram.
  - Done when: report output includes item-level counter variance histograms.
- [ ] `SC-010` Multi-simulation report: min/max variance KPIs.
  - Done when: report includes min and max call variance and item variance values.

### Priority 4 - Documentation and Enablement

- [ ] `SC-016` Document workflow charts and diagrams.
  - Done when: project workflow charts/diagrams are added to docs and linked from the documentation index.

## In Progress

- [ ] No tickets currently in progress.

## Done

- [x] `SC-001` Monte Carlo daily utilisation generation for one or more simulations.
  - Done criteria met: utilisation generation exists and is used in simulation flow.
- [x] `SC-002` Configuration-driven parameters via `config.json`.
  - Done criteria met: runtime configuration is loaded from JSON and drives simulation inputs.
- [x] `SC-003` Work-order schedule creation from planning parameters.
  - Done criteria met: schedule build covers item cycles, package cycle, call horizon, suppression/completion requirements, and shift factors.
- [x] `SC-004` Simulation loop updates operational state.
  - Done criteria met: simulation updates call state, planned/completion days, completion counters, and annual estimate recalculation.
- [x] `SC-005` Export simulation outputs for inspection.
  - Done criteria met: per-run CSV outputs are generated.
- [x] `SC-006` Generate last-run reporting outputs.
  - Done criteria met: markdown and HTML reports are generated under `reports/` with planned-vs-actual counter visuals.

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
