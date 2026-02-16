# Code Standards

## Language and Style

- Target Python 3.10+.
- Follow PEP 8 and use clear, descriptive names.
- Keep functions small and single-purpose where practical.
- Avoid duplicated logic; refactor shared behavior into helpers.

## Environment and Execution

- Use `uv` as the default Python workflow tool.
- Create virtual environments with `uv venv`.
- Install dependencies with `uv pip install -r requirements.txt`.
- Run scripts/tests with `uv run ...` instead of direct `python ...` where practical.

## Typing and Interfaces

- Add type hints for public functions and non-trivial internal helpers.
- Prefer explicit return types.
- Validate external inputs (config/data) near boundaries.
- Raise meaningful exceptions for invalid states.

## Project Structure

- Keep domain logic in `src/simulation/` modules, not in `main.py`.
- Place cross-cutting helper functions in `src/utils/` with purpose-specific modules.
- Minimize side effects in core logic functions.
- Isolate I/O (CSV writes, plotting, logging) from computation when possible.
- Keep configuration parsing centralized.

## Data and State

- Avoid mutating shared DataFrames unless intentional and documented.
- Copy mutable inputs when function behavior depends on isolation.
- Be explicit about units and semantics for counters and rates.
- Preserve consistent column naming across pipeline stages.

## Testing Standards

- Add tests for all bug fixes.
- Add unit tests for:
  - schedule generation
  - call triggering
  - completion handling
  - annual estimate recalculation cadence
- Use deterministic seeds for stochastic behavior in tests.
- Cover both `suppressed=true` and `suppressed=false` paths.

## Quality Gates

- No known runtime exceptions on supported configuration paths.
- No dead imports or unused variables in modified files.
- New code should not add uncontrolled sleeps or debug prints in hot loops.
- Update docs alongside behavior changes.

## Dependency Standards

- Dependencies in `requirements.txt` must be valid installable package names.
- Add only required packages; remove unused dependencies.
- Pin or constrain versions intentionally and document rationale when strict.
