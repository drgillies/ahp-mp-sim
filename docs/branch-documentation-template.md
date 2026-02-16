# Branch Documentation Template

Use this template at branch creation time and keep it updated during implementation.

## Branch Name

`<type/short-description>`

## Branch Goal

State the single primary outcome this branch is expected to deliver.

Example:

`Fix simulation completion counter updates to prevent runtime crashes.`

## Problem Statement

Describe the current issue or gap in 2-4 sentences.

## Scope

### In Scope

- Item 1
- Item 2

### Out of Scope

- Item 1
- Item 2

## Acceptance Criteria

- [ ] Criterion 1
- [ ] Criterion 2
- [ ] Criterion 3

## Technical Plan

1. Step 1
2. Step 2
3. Step 3

## Risks and Mitigations

- Risk: ...
  - Mitigation: ...

## Validation Plan

- Command: `uv run python -m unittest discover -s tests -v`
- Command: `<additional verification command>`
- Expected result: tests pass and no regressions in changed behavior.

## Documentation Updates

- [ ] Update runbook/docs for behavior changes.
- [ ] Update standards if new conventions are introduced.
- [ ] Update known issues if applicable.

## PR Notes

- Linked issue/task: `<id or link>`
- Review focus areas:
  - Area 1
  - Area 2
