---
id: API-05
title: "api: add role-based access control"
module: api
labels: [api, security, stretch]
difficulty: stretch
estimate: 2 days
depends_on: [API-03]
---

## Why this matters

Right now every endpoint returns everything to anyone who asks, and CORS is wide open. A
recruiter should not see client margins; an exec doesn't need individual timesheets. The
architecture has promised RBAC since day one - this is it.

## What "done" looks like

- [ ] Three roles: `recruiter`, `delivery_manager`, `exec`
- [ ] The role arrives with the request (an `X-Role` header is fine for now) and a **missing or
      unknown role is rejected with 401/403** - not quietly treated as the most privileged
- [ ] Each endpoint declares which roles may call it
- [ ] Recruiters cannot see margin or cost-rate fields
- [ ] CORS is narrowed from `*` to the known local origins
- [ ] Tests: each role gets what it should, and is refused what it shouldn't
- [ ] `docs/ARCHITECTURE.md` section 3 updated to describe what was actually built

## Where to work

- `api/app/auth.py` - new
- `api/app/main.py`, every file in `api/app/routers/`
- `api/tests/test_auth.py` - new

## How to approach it

1. A FastAPI **dependency** is the right tool: one function that reads the header, validates the
   role, and raises `HTTPException` otherwise. Endpoints declare it with
   `Depends(require_role("exec"))`.
2. **Default to denying.** An endpoint with no role declared should refuse, not allow. Write the
   test for that first - it's the failure mode that actually bites.
3. Field-level hiding (margin, cost rate) is best done with a separate response model per role
   rather than deleting keys from a dict on the way out. Deleting keys is easy to forget on the
   next endpoint.
4. Narrow CORS to `http://localhost:8080` and `http://localhost:5173`.

## How to check it

```bash
python -m pytest api/tests
```

Try every endpoint in `/docs` with each role, and with no header at all. **No header must fail.**

## Gotchas

- This is not real authentication - a header anyone can set is not a security boundary, and real
  auth (tokens, an identity provider) is a later milestone. Say that clearly in your PR and in
  the architecture doc, so nobody deploys this thinking it's finished.
- Tell the web owner before you merge: every request will need the header, so this breaks the
  dashboard until they add it. Coordinate the two PRs.
