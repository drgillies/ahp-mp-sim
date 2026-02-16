# Git Standards

## Branching

- `main` is always releasable.
- Create short-lived feature branches from `main`.
- Branch names should be descriptive:
  - `feature/<topic>`
  - `fix/<topic>`
  - `chore/<topic>`

## Commits

- Commit messages should be imperative and specific.
- Recommended format:
  - `<type>: <summary>`
  - Example: `fix: prevent scalar astype crash in completion logic`
- Keep commits focused; avoid unrelated file changes in the same commit.
- Do not commit generated artifacts unless explicitly required.

## Pull Requests

- PR title should describe user-visible outcome.
- PR description should include:
  - what changed
  - why it changed
  - how to verify
  - risks or follow-ups
- Link related issue or task when available.
- Request review only after local checks pass.

## Review and Merge

- At least one reviewer approval is required.
- Address feedback with new commits; avoid force-pushing after review unless necessary.
- Use squash merge by default to keep history clean, unless preserving commit history is important.

## Tags and Releases

- Use annotated tags for releases.
- Release notes must summarize behavior changes, fixes, and migration notes.

## Safety Rules

- Never rewrite shared branch history without team agreement.
- Never commit secrets, credentials, or local environment files.
- Use `.gitignore` for local outputs and temporary files.
