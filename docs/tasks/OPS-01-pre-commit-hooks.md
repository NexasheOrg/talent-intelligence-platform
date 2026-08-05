---
id: OPS-01
title: "devops: catch lint failures before they reach CI"
module: devops
labels: [devops, good-first-issue]
difficulty: warm-up
estimate: half a day
depends_on: []
---

## Why this matters

The cycle right now is: push, wait three minutes, CI goes red over import order, push again. A
pre-commit hook catches it in two seconds on your own machine. Small change, and everyone feels
it every day.

This is a good day-one task, and it's how you'll learn what the CI pipeline actually runs.

## What "done" looks like

- [ ] `.pre-commit-config.yaml` running, at minimum: `ruff check`, `ruff format --check` (or
      agree the team doesn't want the formatter), trailing whitespace, end-of-file newline, and
      a large-file guard
- [ ] The hook versions are **pinned**, so it doesn't change under people
- [ ] Setup is one command, documented in `CONTRIBUTING.md`
- [ ] The hooks pass on the repo as it is today - if they don't, fix the repo in the same PR
- [ ] It's opt-in and documented as such: a hook that blocks a commit somebody urgently needs to
      make will just get bypassed with `--no-verify` and resented

## Where to work

- `.pre-commit-config.yaml` - new
- `CONTRIBUTING.md`, `docs/ONBOARDING.md`

## How to approach it

1. Read `.github/workflows/ci.yml` first. The hooks should run **the same checks CI runs**, or
   you've built a second source of truth that will drift.
2. Add the large-file guard deliberately: it's the thing that stops someone accidentally
   committing a database file or a model binary, which is a real risk in this repo.
3. Keep it fast. A hook that takes 30 seconds gets bypassed. Under five is the target.
4. Consider whether the web layer belongs here too - `npm test` is too slow for a hook, but a
   quick lint might not be.

## How to check it

```bash
pip install pre-commit
pre-commit install
pre-commit run --all-files     # must pass on the current repo
```

Then make a deliberately badly-formatted commit and confirm it's stopped.

## Gotchas

- Don't add a hook that reformats every file in the repo on first run. That produces a
  thousand-line diff that hides real changes and makes `git blame` useless. If formatting is
  wanted, that's its own separate, announced PR.
- CI stays the real gate. Hooks are a convenience; someone can always bypass them, so nothing may
  depend on them having run.
