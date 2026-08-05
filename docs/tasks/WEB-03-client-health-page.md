---
id: WEB-03
title: "web: build the Client Health dashboard"
module: web
labels: [web]
difficulty: core
estimate: 2 days
depends_on: [API-03]
---

## Why this matters

Staffing revenue concentrates fast: a handful of clients usually carry most of the margin. When
one of them quietly stops opening roles, nobody notices until the quarter closes. This page is
the early warning.

## What "done" looks like

- [ ] `/clients` renders a real dashboard instead of the placeholder
- [ ] A KPI row: active clients, total margin per hour, clients with no placement in 90 days
- [ ] A chart of margin by client tier
- [ ] A table of clients: name, industry, tier, placements, margin - sortable by margin
- [ ] Loading, error and empty states all handled via `<DataState>`
- [ ] Every chart has its table view (use `<ChartCard>`)
- [ ] A test with a mocked API
- [ ] The `ComingSoon` route for `/clients` is removed from `App.tsx`
- [ ] A screenshot in the PR

## Where to work

- `web/src/pages/ClientHealth.tsx` - new
- `web/src/pages/ClientHealth.test.tsx` - new
- `web/src/App.tsx` - swap the route
- `web/src/lib/types.ts` - add the response types
- `web/src/pages/Overview.tsx` - mark it Built in `DASHBOARDS`

## How to approach it

1. **Talk to whoever owns API-03 first.** Agree the response shape between you before either of
   you writes code. Fifteen minutes now saves a day of rework.
2. While you wait for the endpoint, build the page against a hardcoded object of the agreed
   shape. Delete it once the endpoint exists.
3. Copy `pages/Utilization.tsx`. It already shows the pattern: `useApi` → `<DataState>` →
   `<ChartCard>` → a chart from `components/charts/`.
4. For "at risk", pick a rule you can defend and **write it on the page** so nobody has to guess
   what the number means.

## How to check it

```bash
cd web && npm test && npm run build
```

Click every state: normal, API stopped (`docker compose stop api`), and a client with no
placements.

## Gotchas

- Don't invent a colour. `components/charts/theme.ts` has the validated ones.
- Client tier (Strategic / Growth / Standard) is ordered, so an ordinal ramp is allowed there -
  see how `pages/Funnel.tsx` does it. Industry is **not** ordered: one colour for all bars.
- "At risk" is a judgement, not a fact. Label it as a rule, not as truth.
