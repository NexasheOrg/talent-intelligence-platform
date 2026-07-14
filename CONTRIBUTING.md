# Contributing

This is how we work so five people can move without stepping on each other. If you're new,
read this once fully.

## Branching & PRs
- `main` is always deployable. Never push to it directly.
- Branch per task: `feature/<area>-<short-desc>`, e.g. `feature/api-bench-endpoint`.
- Open a PR early (draft is fine). Small PRs > big PRs.
- Every PR needs **one review**. Juniors' first few PRs are reviewed by Laya or Praveen.
- CI must be green before merge.

## Issues
- Every piece of work has an issue. Labels: `data-platform`, `infra`, `api`, `web`, `ml`,
  `ai-assistant`, `docs`, plus `good-first-issue` for juniors.
- Assign yourself before you start. Comment when blocked.

## Commits
- Present tense, scoped: `api: add RBAC middleware`, `data-platform: build silver timesheets`.

## The golden rules
1. **No real or customer data in git — ever.** Only the synthetic seed generator.
2. **Don't break the gold schema** without a PR + updating `docs/ARCHITECTURE.md`.
3. **Your slice must run locally** from seed data before you call it done.
4. Write a test for anything with logic. A dashboard needs a screenshot in the PR.

## Local dev
```bash
python data/seed/generate_seed.py
docker compose up        # (added in Milestone 0)
```

## Definition of done
Runs locally from seed · has a test or a screenshot · reviewed · CI green · issue closed.
