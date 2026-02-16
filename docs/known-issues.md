# Known Issues

This file tracks observed defects and technical risks in the current codebase.

## Resolved Defects

- Completion update no longer uses scalar `.astype` calls in `src/simulation/montecarlo.py`.
- Non-suppressed schedule sorting now uses existing columns in `src/simulation/montecarlo.py`.
- Multi-simulation runs now return combined simulation DataFrames in `src/simulation/montecarlo.py`.
- `annual_estimate_recalculate_after_days` is now carried through work-order records.
- `src/simulation/parameters.py` now handles optional `basic_start_date`.
- `requirements.txt` now uses `PyYAML` instead of `yaml`.

## Performance Risks

- Simulation still relies on row-wise DataFrame `.apply` for recalculation logic and may be slow at very large scales.
- CSV export is enabled by default in `run_simulation`; callers should disable it for pure in-memory runs.

## Test Coverage Gaps

- Current tests focus on schedule generation and core simulation correctness paths.
- Additional tests are still needed for edge cases around shift-factor behavior and completion-requirement gating.
