---
id: AI-04
title: "web + ai: build the Ask your data page"
module: ai-assistant
labels: [ai-assistant, web]
difficulty: core
estimate: 2 days
depends_on: [AI-01]
---

## Why this matters

The assistant works but has no front door - you can only reach it with `curl`. This is the page
that makes it a product, and it's a good task if you want to touch both frontend and backend.

## What "done" looks like

- [ ] `/ask` renders a real page instead of the placeholder
- [ ] One input box; Enter or a button submits
- [ ] The answer appears, **with the SQL that produced it** shown alongside
- [ ] Multi-row answers render as a table
- [ ] An unanswerable question shows the assistant's own suggestions rather than an error
- [ ] Example questions are shown as clickable chips, loaded from `/api/assistant/examples`
- [ ] Loading and error states handled
- [ ] A test with a mocked API covering: a good answer, and a refusal
- [ ] The `ComingSoon` route for `/ask` is removed from `App.tsx`

## Where to work

- `web/src/pages/AskYourData.tsx` - new
- `web/src/pages/AskYourData.test.tsx` - new
- `web/src/App.tsx`, `web/src/lib/types.ts`, `web/src/pages/Overview.tsx`
- `web/src/lib/api.ts` - it currently only does GET; you need a POST helper

## How to approach it

1. Run the assistant first and poke it in `/docs`, so you know the response shape before you
   build against it.
2. `lib/api.ts` needs a `postJson` next to `getJson`. Follow the existing shape - same error
   handling, same relative-path rule.
3. The proxy is already wired: `/api/assistant/*` reaches port 8100 in both Vite and nginx. You
   shouldn't need to touch either.
4. **Show the SQL prominently, not hidden behind a "details" toggle.** It's the feature that
   makes the answer trustworthy - an answer nobody can check is worse than no answer, because
   people act on it.

## How to check it

```bash
cd web && npm test && npm run build
```

Try: a question it knows, a question it doesn't, and the assistant stopped entirely.

## Gotchas

- Don't let it look like a chatbot. It answers one question at a time from a fixed set of
  capabilities; a chat UI promises memory and conversation it doesn't have, and users will
  immediately try both.
- Never render the answer as HTML. It's derived from user input - display it as text.
