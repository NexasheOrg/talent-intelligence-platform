---
id: ML-01
title: "ml: give the seed data a realistic attrition signal"
module: ml
labels: [ml, good-first-issue]
difficulty: warm-up
estimate: 1 day
depends_on: []
---

## Why this matters

The roadmap wants an attrition-risk model. You can't train one: **the seed data never records
whether anyone left.** There is no label, so there is nothing to predict.

That's the real first task, and noticing it is a large part of the job. Before this, the "risk
score" in the API is a hand-written heuristic in `api/app/risk.py` - a placeholder, not a model.

This is your day-one task.

## What "done" looks like

- [ ] `dim_consultant` gains a leaver signal - at minimum `left_date` (null if still employed),
      and `status` can include `left`
- [ ] The generator makes leaving **depend on things that plausibly cause it**, so a model has
      something to find: long bench time, low pay relative to peers, short tenure, seniority
- [ ] The relationship is noisy, not deterministic. If bench > 90 days always means leaving, any
      model scores 100% and you've learned nothing
- [ ] Roughly a believable rate - single-digit to low-teens percent per year, not 60%
- [ ] `gold_schema.sql` and `docs/ARCHITECTURE.md` updated in the same PR
- [ ] Quality checks: no `left_date` before `hire_date`, none in the future
- [ ] `ml/src/features.py` can load the new label

## Where to work

- `data/seed/generate_seed.py`
- `data-platform/models/gold_schema.sql`
- `data-platform/quality/checks.py`
- `docs/ARCHITECTURE.md`

## How to approach it

1. Write down the story first: "consultants are more likely to leave if they've been benched a
   long time, are paid below the median for their seniority, or joined recently." Then encode
   *that*.
2. Turn it into a probability per consultant, then sample. `random.random() < probability` -
   not an `if` that decides outright.
3. Keep `random.seed(42)`. Everyone must generate identical data, or two people comparing model
   scores are comparing different worlds.
4. Sanity-check the output: what fraction left? Does the leave rate rise with bench time? A quick
   printed cross-tab is enough.

## How to check it

```bash
python data/seed/generate_seed.py
python data-platform/load_seed.py
python data-platform/quality/checks.py
python ml/src/features.py
```

## Gotchas

- **Don't make the label a clean function of one feature.** That's the classic mistake: the model
  scores 99%, everyone is delighted, and it has learned nothing but your own if-statement.
- Talk to the data-platform owner before changing the schema - you're both editing
  `gold_schema.sql` and they need to know.
- This is synthetic data designed to be learnable. Say so in the PR: a model that works here has
  not been validated against reality.
