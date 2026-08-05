---
id: WEB-01
title: "web: make the consultants table sortable"
module: web
labels: [web, good-first-issue]
difficulty: warm-up
estimate: half a day
depends_on: []
---

## Why this matters

"Who's been on the bench longest?" is the first question a delivery manager asks, and right now
the only way to answer it is to page through 300 rows. Clicking a column header should sort by
it.

This is your day-one task. It's deliberately small: the point is to get one change merged and
see the whole loop - branch, code, test, PR, review.

## What "done" looks like

- [ ] Clicking a column header sorts the table by that column
- [ ] Clicking the same header again reverses the direction
- [ ] The current sort column and direction are visible (an arrow is fine)
- [ ] Headers are real `<button>`s, so they work with the keyboard and screen readers
- [ ] `aria-sort` is set on the sorted column
- [ ] A test covers "click sorts ascending, click again sorts descending"

## Where to work

- `web/src/pages/Consultants.tsx` - the table
- `web/src/pages/Consultants.test.tsx` - new file; copy `pages/Overview.test.tsx`

## How to approach it

1. Run the app and look at the page first. `npm run dev` in `web/`.
2. Hold the sort in state: `const [sort, setSort] = useState({ key: 'name', direction: 'asc' })`.
3. Sort a **copy** of `data.rows` before rendering - `[...rows].sort(...)`, never `rows.sort(...)`,
   which mutates React's state and causes bugs that look like the UI "not updating".
4. Watch out for `days_on_bench`, which is `null` for anyone not on the bench. Decide where
   nulls go and be consistent - they should not scatter through the middle.
5. Add the test.

## How to check it

```bash
cd web
npm test
npm run build      # typecheck must pass too
```

Then click through it in the browser, including with the keyboard: Tab to a header, press Enter.

## Gotchas

- This sorts **the page you're looking at**, not all 300 consultants. That's a real limitation
  and it's fine for now - server-side sorting is API-02. Say so in your PR rather than leaving
  the next person to discover it.
- Don't add a sorting library for this. It's a comparison function.
