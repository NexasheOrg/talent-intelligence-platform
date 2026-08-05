---
id: DATA-03
title: "data-platform: add stage history so the funnel shows real conversion"
module: data-platform
labels: [data-platform]
difficulty: core
estimate: 2 days
depends_on: []
---

## Why this matters

The Placement Funnel currently shows **where candidates are**, not **how many get through each
step** - and the page says so, because `fact_pipeline` only stores one current stage per
candidate. "40% of candidates are at submitted" and "40% of submissions convert to interview"
are completely different numbers, and only the second one is useful.

Fixing this is a data-model change, which is why it's here and not in the API.

## What "done" looks like

- [ ] The seed generator produces a **row per stage transition** with its date, not one row per
      candidate
- [ ] A candidate's history is coherent: you can't reach `offer` without passing `interview`,
      dates only move forward, and `rejected` ends the journey
- [ ] The gold schema is updated, and so is `docs/ARCHITECTURE.md`, in the same PR
- [ ] `/api/funnel` can compute true stage-to-stage conversion from it
- [ ] Quality checks cover the new invariants (no out-of-order dates, no impossible jumps)
- [ ] Existing API tests still pass, or are updated with the reason in the PR

## Where to work

- `data/seed/generate_seed.py`
- `data-platform/models/gold_schema.sql`
- `data-platform/quality/checks.py`, `data-platform/tests/`
- `docs/ARCHITECTURE.md`

## How to approach it

1. **Decide the model first and write it in the issue before coding.** Two reasonable options:
   keep `fact_pipeline` as the current state and add `fact_pipeline_history`; or make
   `fact_pipeline` the transition log and derive current state. Both work. Pick one, say why.
2. Generate realistic drop-off: most candidates stop at submitted, fewer reach interview, fewer
   still get an offer. A funnel where everyone converts is not a funnel.
3. Add the quality checks as you go - they're how you'll know the generator is producing coherent
   histories.
4. **Talk to the API owner before merging.** They need to change `/api/funnel`, and the web owner
   needs to update the caveat on the page. Ideally the three PRs land together.

## How to check it

```bash
python data/seed/generate_seed.py
python data-platform/load_seed.py
python data-platform/quality/checks.py
python -m pytest
```

Then check by hand that conversion rates are monotonic: the count reaching each stage should
never go up as you move down the funnel.

## Gotchas

- This changes the gold schema, which four other people build on. Announce it, and update the
  architecture doc in the same PR - that's the rule.
- Watch the row count. A transition log is several times bigger than one row per candidate;
  make sure the API's funnel query still counts candidates, not transitions.
