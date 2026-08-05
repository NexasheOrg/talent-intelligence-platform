# Onboarding

Welcome to the team. This takes you from "the app runs" to "I've shipped a change".

**Haven't got it running yet?** Start with [WINDOWS-SETUP.md](WINDOWS-SETUP.md) (or
[RUN-WITHOUT-DOCKER.md](RUN-WITHOUT-DOCKER.md) if Docker won't install), then come back here.

Commands below are shown for **PowerShell on Windows** first, with the macOS/Linux version
underneath. Run them from the project folder.

---

## 1. What this app is

A **Talent & Delivery Intelligence Platform**: the analytics brain for a staffing or
recruitment company. It pulls together the numbers that decide whether the business makes
money - who's on the bench and for how long, how candidates move from submission to placement,
whether hours get billed, which clients are healthy.

It has five parts, and **each of you owns one**:

| Folder | What it does | In one sentence |
|---|---|---|
| [`data-platform/`](../data-platform) | shapes raw data into clean tables | the numbers everyone else trusts |
| [`api/`](../api) | serves those tables over HTTP | the only thing that talks to the database |
| [`web/`](../web) | the dashboards people look at | the product surface |
| [`ml/`](../ml) | predicts bench duration / attrition risk | the "who's at risk" number |
| [`ai-assistant/`](../ai-assistant) | answers plain-English questions | "how many consultants know Python?" |

Everything runs against **synthetic (fake) data** generated on your laptop. No real or customer
data is ever needed to develop, and none may ever be committed. That's non-negotiable.

Worth skimming next: the [README](../README.md) and [ARCHITECTURE](ARCHITECTURE.md).

---

## 2. Get your bearings in the running app

Before changing anything, look at what's there:

- <http://localhost:8080> - the dashboard. Click every page in the left nav.
- <http://localhost:8000/docs> - the API's own documentation, generated from the code. Every
  endpoint has a **Try it out** button. Use it; it's the fastest way to understand the data.
- <http://localhost:8100/docs> - the assistant, same idea.

Three dashboards are built. Three are marked `todo` - open one. It tells you what to build,
which endpoint it needs, and which existing file to copy. Those are real tasks.

---

## 3. Working on the code, with hot reload

`START-HERE.bat` runs the whole app, but it doesn't pick up your edits until you restart it.
While you're actively writing code you want the opposite: save a file, see the change.

Run **only the layer you're changing**.

### The dashboard (`web/`)

```powershell
cd web
npm install     # first time only
npm run dev
```

Open the address it prints - usually <http://localhost:5173>. Save a file and the browser
updates instantly. It reads from the API on port 8000, so leave the Docker stack running (or
just its API: `docker compose up -d db loader api`).

### The Python layers (`api/`, `data-platform/`, `ml/`, `ai-assistant/`)

Python packages go in a **virtual environment** ("venv") - a private folder of packages that
belongs to this project only, so projects can't break each other. Create it once:

```powershell
python -m venv .venv
.venv\Scripts\activate
pip install -r api\requirements.txt -r requirements-dev.txt
```

```bash
# macOS / Linux
python3 -m venv .venv
source .venv/bin/activate
pip install -r api/requirements.txt -r requirements-dev.txt
```

You'll know it worked when your prompt starts with `(.venv)`. Every new terminal needs the
activate line again; `deactivate` when you're done. `.venv/` is git-ignored, so it never gets
committed.

Then run the API against the database, with auto-reload:

```powershell
docker compose up -d db loader
$env:DATABASE_URL = "postgresql://tip:tip@localhost:5433/tip"
python -m uvicorn app.main:app --app-dir api --port 8000 --reload
```

```bash
# macOS / Linux
docker compose up -d db loader
DATABASE_URL=postgresql://tip:tip@localhost:5433/tip \
  python -m uvicorn app.main:app --app-dir api --port 8000 --reload
```

No Docker? Skip the `docker compose` line and use
`sqlite:///data/local/tip.db` as the `DATABASE_URL` - see
[RUN-WITHOUT-DOCKER.md](RUN-WITHOUT-DOCKER.md).

Port **5433** is deliberate: Postgres is mapped to 5433 on your machine so it can't clash with
another Postgres on the usual 5432.

That terminal stays busy while the server runs. Open a second one for anything else.

---

## 4. Running the tests

Before you open a pull request, run the tests for your layer. CI runs them anyway - finding out
here is faster than finding out there.

```powershell
python -m pytest            # all the Python tests
python -m pytest api\tests  # just one layer
cd web; npm test            # the dashboard
```

And the data-quality checks, if you touched anything in `data-platform/`:

```powershell
python data-platform\quality\checks.py
```

**Read the existing tests before writing yours.** Each layer's test files start with a comment
explaining the pattern that layer uses. Copying a good test is a completely legitimate way to
write one.

---

## 5. Making a change and getting it merged

1. **Pick your task** from [TASKS.md](TASKS.md). Your lead will have assigned you a module.
   Start with the `-01` task in your module - it's designed to be finishable on day one.
2. **Make a branch.** In GitHub Desktop: `Current Branch → New Branch`. Name it
   `feature/<area>-<what>`, e.g. `feature/web-client-health`.
3. **Write the change.** Small steps, checking the app as you go.
4. **Run the tests.** See above.
5. **Commit and push.** GitHub Desktop does both with buttons. Write the message as what it
   does: `api: add client health endpoint`.
6. **Open a Pull Request** and ask for a review. Include a screenshot if you changed the UI.
7. **Respond to review comments.** Being asked to change something is the normal outcome of a
   review, not a criticism. Everyone's PRs get comments.

Full rules: [CONTRIBUTING.md](../CONTRIBUTING.md).

### Keep pull requests small

A PR that changes 40 files gets a slow, shallow review. A PR that changes 3 gets a fast,
useful one. If your task feels too big for one PR, split it - and say so in the issue.

---

## 6. When something breaks

Work down this list before asking, but **do ask** - the 15-minute rule below is real.

| What you see | Usually means |
|---|---|
| `docker: command not found` | Docker Desktop isn't installed or isn't open. |
| Port already in use (8080 / 8000 / 5433 / 5173) | An old run is still going. Double-click `STOP.bat`. |
| `error: externally-managed-environment` | You're installing Python packages outside a venv. See section 3. |
| `command not found: pip` | Activate your venv first. Outside one, macOS calls it `pip3`. |
| `ModuleNotFoundError: No module named 'app'` | Run uvicorn with `--app-dir api` from the project root. |
| Dashboard says "Could not reach the API" | The API isn't running, or it's still starting. Check <http://localhost:8000/health>. |
| A chart shows axes but no bars or line | Almost always no data, not a chart bug - check the endpoint in `/docs`. |
| Changes not showing in the Docker app | Docker runs a built copy. Use hot reload (section 3), or `STOP.bat` then `START-HERE.bat`. |
| Tests pass locally, fail in CI | Usually a file you forgot to commit, or SQLite being more forgiving than Postgres. |

To see why a container failed:

```powershell
docker compose logs api
docker compose logs loader
```

**The 15-minute rule:** if you've been stuck on the same error for 15 minutes, post it in the
team chat with the exact error text. That is what everyone here does. Silently losing an
afternoon is the only version of this that's a problem.

---

## 7. Things that will get your PR sent back

Not to be harsh - just so you know before you write it:

- **Real or customer data committed.** Only the synthetic generator. This one is serious.
- **A changed gold schema without a PR note.** Four other people build on those table names;
  changing one silently breaks them. Update [ARCHITECTURE.md](ARCHITECTURE.md) in the same PR.
- **SQL that only works on Postgres.** Everything must run on SQLite too, so nobody is blocked
  on Docker. See the note at the top of `api/app/db.py`.
- **A user's input pasted into a SQL string.** Always use `?` parameters. See
  `api/app/routers/consultants.py`.
- **A new number on screen with no test.** Anything with logic needs a test; a dashboard change
  needs a screenshot in the PR.
- **A dead `console.log` or `print()`** left in the code.

---

## 8. Where to go next

- [TASKS.md](TASKS.md) - find your task.
- The README in **your** layer's folder. It says what's built and what's next.
- [ARCHITECTURE.md](ARCHITECTURE.md) - how the pieces fit, and the gold-schema contract.

Ask questions early and often. In your first two weeks, asking too few is a much bigger problem
than asking too many.
