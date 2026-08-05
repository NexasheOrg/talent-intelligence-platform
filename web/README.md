# web

The product surface: the dashboards people actually look at. Talks to `api/` for data and
`ai-assistant/` for natural-language queries.
**Stack:** React, TypeScript, Vite, Recharts.

## What's here

```
src/
  App.tsx              the shell: sidebar nav + routes
  lib/
    api.ts             the ONLY place that calls fetch. Use useApi(), not fetch()
    types.ts           TypeScript mirrors of the API's response models
    format.ts          number/date formatting - keep it out of components
  components/
    Card.tsx           Card, Kpi, Pill
    DataState.tsx      loading / error / empty, handled once for every page
    ChartCard.tsx      a chart panel + its table view
    ConsultantDetail.tsx
    charts/
      theme.ts         colours and chart rules - READ THIS before adding a chart
      LineTrend.tsx    single-series trend line
      StackedBars.tsx  two-series stacked columns
      CategoryBars.tsx horizontal bars for category comparison
  pages/
    Overview.tsx       home
    Utilization.tsx    the reference page for charts - copy this one
    Funnel.tsx
    Consultants.tsx    the reference for filters + table + pagination
    ComingSoon.tsx     placeholder that tells you what to build
```

**Built:** Overview · Utilization & Bench · Placement Funnel · Consultants.
**Not built:** Client Health · Timesheet & Billing · Ask your data. Each renders a brief in the
running app saying what it needs and what to copy - tasks `WEB-03`, `WEB-04`, `AI-04`.

## Adding a page

1. Write it in `pages/`, copying `Utilization.tsx` (charts) or `Consultants.tsx` (tables).
2. Add a `<Route>` and a `NAV` entry in `App.tsx`.
3. Add the API types to `lib/types.ts`.
4. Add a test - copy `pages/Overview.test.tsx`.

## Conventions that matter

- **Never call `fetch` in a component.** Use `useApi()`. That's what gives every page the same
  error handling and loading behaviour.
- **Never hardcode a colour in a chart.** Import from `charts/theme.ts`. Those hexes were
  validated for colour-vision deficiency against this app's background; a hand-picked one
  hasn't been.
- **Every chart gets a table view.** `ChartCard` gives you one for free. A chart on its own
  excludes screen-reader users and anyone who needs an exact number.
- **Wrap fetched content in `<DataState>`.** It forces you to handle the empty case, which is
  the one reviewers always catch.
- Use relative `/api/...` paths, never `http://localhost:8000` - nginx and Vite both proxy
  `/api`, and a hardcoded port breaks one of them.

## Running it

```bash
cd web
npm install     # first time only
npm run dev     # http://localhost:5173, reloads on save
```

It needs the API on port 8000 - `docker compose up -d db loader api` is enough.

```bash
npm test          # vitest
npm run build     # typecheck + production build; CI runs this
```
