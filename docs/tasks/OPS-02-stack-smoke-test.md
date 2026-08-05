---
id: OPS-02
title: "devops: smoke-test the whole stack in CI"
module: devops
labels: [devops]
difficulty: core
estimate: 1-2 days
depends_on: []
---

## Why this matters

CI currently tests each layer in isolation. Nothing checks that `docker compose up` actually
produces a working app - so a broken Dockerfile, a wrong nginx route or a service that can't
reach the database gets discovered by the next person who tries to start it, usually on a
Monday morning.

Everything the freshers do begins with the stack starting. This is the check that protects that.

## What "done" looks like

- [ ] A script that starts the full stack, waits for it to be ready, and verifies:
      the API answers `/health`; `/api/utilization` returns non-zero consultants; the assistant
      answers a known question; nginx serves the dashboard; and `/api/` and `/api/assistant/`
      both route to the right service through nginx
- [ ] It tears the stack down afterwards, including on failure
- [ ] It fails with a **useful message and the failing container's logs**, not just a red X
- [ ] Runs in CI on every PR
- [ ] Runs locally with one command
- [ ] Total runtime under about five minutes, with Docker layer caching

## Where to work

- `scripts/smoke-test.sh` - new
- `.github/workflows/ci.yml` - a new job
- `scripts/start.sh` - reuse its wait-for-URL helper rather than writing a second one

## How to approach it

1. **Poll, never sleep.** `sleep 60` is both slower than it needs to be and flaky when the
   runner is loaded. `scripts/start.sh` already has the wait-for-URL pattern - reuse it.
2. Check something meaningful, not just a 200. `/api/utilization` returning
   `total_consultants: 0` means the loader silently failed, and a status-code-only check would
   pass happily.
3. Test **through nginx** on port 8080, not directly against the services. The proxy routes are
   exactly the kind of thing that breaks silently, and only the proxy path proves them.
4. `docker compose logs` on failure, in a `trap`, so a red build tells you why without a rerun.

## How to check it

```bash
./scripts/smoke-test.sh
```

Then break something on purpose - a typo in a proxy_pass, a wrong port - and confirm it fails
with a message that names what broke.

## Gotchas

- Always tear down, even when the test fails. A `trap ... EXIT` handles it; without one, a
  failing run leaves containers holding ports on the next run.
- Don't just assert the containers are *running*. A container can be up and the app broken - that
  is the exact failure this job exists to catch.
