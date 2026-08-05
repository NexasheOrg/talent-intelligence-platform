---
id: WEB-05
title: "web: add a light theme"
module: web
labels: [web, stretch]
difficulty: stretch
estimate: 1-2 days
depends_on: []
---

## Why this matters

The app is dark-only. People present these dashboards on projectors and read them next to a
window, where dark themes wash out. This task is also the best way to learn why the chart
colours are the way they are.

## What "done" looks like

- [ ] A toggle switches between light and dark
- [ ] The choice is remembered across a refresh (`localStorage`)
- [ ] It follows the OS setting on first visit (`prefers-color-scheme`)
- [ ] Both themes are readable: text, chart marks, axes, borders, focus rings
- [ ] Chart colours are **re-validated against the light surface**, not just lightened by eye
- [ ] The validation results are written into `charts/theme.ts` as a comment, as the dark ones are
- [ ] A test that toggling changes the theme and it survives a remount

## Where to work

- `web/src/styles.css` - the tokens are already at the top under `:root`
- `web/src/components/charts/theme.ts` - the chart colours
- `web/src/App.tsx` - the toggle

## How to approach it

1. Define light values for every token in `:root`, scoped under `:root[data-theme="light"]`.
   Set the attribute on `<html>` from React.
2. Charts are the hard part. Recharts needs real values, not CSS variables, so `theme.ts` has to
   return a different set per theme - a hook or a context, read at render time.
3. **Do not just lighten the dark hexes.** A colour that clears contrast on `#17222e` may fail
   on a white surface, and a pair that's distinguishable under colour-vision deficiency on one
   background may not be on the other. Pick the light steps deliberately and check them.
4. Check, at minimum: every series colour clears 3:1 against the light panel colour, and the two
   series colours are still clearly distinguishable from each other.

## How to check it

```bash
cd web && npm test && npm run build
```

Then look at every page in both themes, including the loading and error states, and the tooltip.
Put before/after screenshots of both in the PR.

## Gotchas

- The comment at the top of `charts/theme.ts` explains what the current numbers mean. Read it
  before changing anything there.
- Don't ship a theme where only the background changed. Half-themed is worse than dark-only,
  because it looks broken rather than deliberate.
