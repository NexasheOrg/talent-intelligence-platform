---
id: WEB-02
title: "web: keep filters in the URL so views can be shared"
module: web
labels: [web]
difficulty: core
estimate: half a day
depends_on: []
---

## Why this matters

Right now, if you filter to benched Senior consultants and send someone the link, they get the
unfiltered page. Filters that live in the URL can be bookmarked, shared in chat, and survive a
refresh - which is how people actually use a dashboard.

## What "done" looks like

- [ ] Changing search, status, seniority or page updates the URL, e.g.
      `/consultants?status=bench&seniority=Senior&page=2`
- [ ] Opening that URL directly restores exactly that view
- [ ] The browser Back button steps back through filter changes
- [ ] Refreshing keeps the filters
- [ ] Empty filters are left out of the URL, not written as `?q=&status=`
- [ ] A test asserts that a URL with parameters renders the filtered view

## Where to work

- `web/src/pages/Consultants.tsx`
- `web/src/pages/Consultants.test.tsx`

## How to approach it

1. `useSearchParams` from `react-router-dom` replaces the `useState` calls for the filters.
   It works like `useState` but reads and writes the query string.
2. Keep the **search box** on local state and only push the debounced value into the URL -
   otherwise every keystroke becomes a history entry and Back becomes useless.
3. `page` comes out of the URL as a string. Parse it, and handle `?page=abc` without crashing.
4. In tests, wrap the page in `<MemoryRouter initialEntries={['/consultants?status=bench']}>`.

## How to check it

- Filter to something, copy the URL, open it in a new tab. Same view?
- Change three filters, then press Back three times.
- Try a hand-written nonsense URL: `?page=-4&status=nonsense`. It should show something sensible
  rather than an error.

## Gotchas

- Two sources of truth for the same value is the classic bug here. The URL should be the truth;
  state that mirrors it will drift.
- `setSearchParams` replaces the whole query string. Preserve the parameters you aren't changing.
