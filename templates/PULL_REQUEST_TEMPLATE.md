## Type

- [ ] `feat` — new feature
- [ ] `fix` — bug fix
- [ ] `chore` — maintenance / dependency update
- [ ] `refactor` — no behaviour change
- [ ] `docs` — documentation only
- [ ] `test` — tests only
- [ ] `style` — formatting, no logic change

## Summary

Brief explanation of what this PR does and why it is needed.

## Related issue

Closes #[issue-number]

## Changes

- Added ...
- Modified ...
- Fixed ...

## Quality gates

- [ ] `ruff .` passes
- [ ] `black --check .` passes
- [ ] `pytest -x --cov=genai_project_template --cov-fail-under=20` passes
- [ ] Coverage did not decrease from baseline
- [ ] Failing test was written **before** implementation (TDD)
- [ ] `tests/` still mirrors `src/` exactly — structure not broken
- [ ] No new `MagicMock` on LangGraph `TypedDict` state

## Branch checklist

- [ ] Branched from `develop` (not `main`)
- [ ] Rebased onto latest `develop` before opening this PR: `git fetch origin && git rebase origin/develop`
- [ ] No direct commits to `develop` or `main`
- [ ] Commit messages follow `feat(scope): description` format, under 72 chars

## Screenshots

<!-- Required for any UI or graph visualisation changes -->
