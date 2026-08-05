---
id: OPS-03
title: "devops: get credentials out of docker-compose.yml"
module: devops
labels: [devops, security]
difficulty: core
estimate: 1 day
depends_on: []
---

## Why this matters

The database password is `tip`, written in plain text in `docker-compose.yml` and copied into
three services. That's fine for a local toy and completely unacceptable the moment this touches a
real environment - and the habit is what carries forward, so it's worth fixing while the stakes
are zero.

## What "done" looks like

- [ ] Configuration comes from environment variables with sensible local defaults
- [ ] A committed `.env.example` documents every variable and what it's for
- [ ] `.env` is git-ignored (check: it already is - verify, don't assume)
- [ ] `docker-compose.yml` reads from `.env` rather than hardcoding
- [ ] The connection string is defined **once**, not repeated per service
- [ ] `START-HERE.bat` and `scripts/start.sh` still work with no `.env` present - a fresher must
      not have to create a config file before the app runs
- [ ] A missing **required** variable fails with a clear message naming the variable
- [ ] Documented in `docs/ONBOARDING.md` and `README.md`

## Where to work

- `.env.example` - new
- `docker-compose.yml`
- `api/app/config.py` - new, or extend `db.py`
- `.gitignore` - verify

## How to approach it

1. **Local defaults must keep working with zero setup.** The whole Windows onboarding story is
   "double-click and it runs" - if this task breaks that, it's a net loss however correct it is.
   Default to the current values; let `.env` override.
2. Separate the two kinds of setting: things that differ per environment (URLs, ports) and things
   that are genuinely secret (passwords, API keys). Only the second kind needs care.
3. Compose reads `.env` from the project root automatically - `${POSTGRES_PASSWORD:-tip}` gives
   you override-with-default in one line.
4. Fail loudly for anything required with no safe default. A service that silently starts with
   the wrong config is worse than one that refuses to start.

## How to check it

```bash
docker compose config      # shows the resolved values - check nothing is empty
./scripts/start.sh         # must still work with no .env at all
cp .env.example .env       # then edit a value and confirm it takes effect
```

## Gotchas

- **Don't commit a real `.env`.** Not once, not "temporarily" - it lives in git history forever.
  Only `.env.example`, with placeholder values.
- Don't log the resolved configuration at startup. That's how passwords end up in CI output.
- This is local-development hygiene, not production secret management. Real deployments need a
  secret store - note that in the PR so nobody thinks this box is ticked.
