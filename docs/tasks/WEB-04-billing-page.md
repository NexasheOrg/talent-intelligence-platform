---
id: WEB-04
title: "web: build the Timesheet & Billing dashboard"
module: web
labels: [web]
difficulty: core
estimate: 2 days
depends_on: [API-04]
---

## Why this matters

Hours that are worked but never logged are hours that are never invoiced. In a staffing business
that is money walking out of the door every Friday, and it's invisible unless someone builds
this page.

## What "done" looks like

- [ ] `/billing` renders a real dashboard instead of the placeholder
- [ ] Headline number: consultants with no timesheet for the most recent week
- [ ] A trend of billable vs bench hours over the available weeks
- [ ] A list of who is missing a timesheet, so someone can chase them
- [ ] Loading, error and empty states handled
- [ ] Table view on every chart
- [ ] A test with a mocked API
- [ ] The `ComingSoon` route for `/billing` is removed
- [ ] A screenshot in the PR

## Where to work

- `web/src/pages/Billing.tsx` - new
- `web/src/pages/Billing.test.tsx` - new
- `web/src/App.tsx`, `web/src/lib/types.ts`, `web/src/pages/Overview.tsx`

## How to approach it

1. Agree the response shape with whoever owns API-04 before writing code.
2. `StackedBars` already does billable-vs-bench over time - see `pages/Utilization.tsx`.
   Reuse it rather than building a new chart.
3. The missing-timesheets list is a table. `pages/Consultants.tsx` is the pattern.
4. Make the empty state a good one: "Everyone has submitted" is a success, and should read like
   one, not like a broken page.

## How to check it

```bash
cd web && npm test && npm run build
```

## Gotchas

- The seed generates timesheets only for **placed** consultants, so "missing" already means
  something specific. Check what the endpoint actually counts before you label the number, and
  write the definition on the page.
- Don't put hours and a percentage on the same chart with two y-axes. Two measures at different
  scales means two charts. This is the single most common dashboard mistake.
